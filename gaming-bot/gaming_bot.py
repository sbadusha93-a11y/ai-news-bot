#!/usr/bin/env python3

import os
import sys
import re
import random
import argparse
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

from gaming_news import fetch_gaming_news, gaming_news_to_script
from video_maker import create_gaming_video, create_shorts
from thumbnail_maker import generate_thumbnail


CLICKABLE_PREFIXES = [
    "BREAKING: {}",
    "{} - You Won't Believe This",
    "MIND BLOWN: {}",
    "Just In: {}",
    "This Changes Everything: {}",
    "HYPE: {}",
    "INSANE: {}",
]


def _generate_title(news_items):
    top = news_items[0]["title"] if news_items else "Gaming News Today"
    short = re.sub(r"[^a-zA-Z0-9 ]", "", top)[:55].strip()
    prefix = random.choice(CLICKABLE_PREFIXES)
    title = prefix.format(short)[:95]
    date = datetime.now().strftime("%b %d")
    return f"{title} | Gaming News {date}"


def generate_description(news_items):
    top_title = news_items[0]["title"] if news_items else "Gaming News"
    lines = [
        f"🎮 {top_title}",
        "",
        "🔥 The LATEST gaming news you NEED to know today!",
        "",
        "📌 Timestamps:",
    ]
    for i, item in enumerate(news_items, 1):
        title = item["title"][:80]
        source = item.get("source", "Gaming News")
        lines.append(f"{i}. {title} - {source}")
    lines.append("")
    lines.append("👍 Which game are you most excited about? Comment below!")
    lines.append("🔔 Subscribe for daily gaming news: https://www.youtube.com/@GamingNews")
    lines.append("")
    lines.append(f"📅 Published: {datetime.now().strftime('%B %d, %Y')}")
    lines.append("")
    lines.append("#GamingNews #Gaming #PlayStation #Xbox #Nintendo #PCGaming #GameNews #VideoGames #Esports #GameUpdate #GamingCommunity #ConsoleWars #GameReveal #GameLaunch")
    return "\n".join(lines)


def get_hook(news_items):
    top = news_items[0] if news_items else {}
    title = top.get("title", "Gaming")
    source = top.get("source", "")
    hooks = [
        f"Hey gamers, you won't believe what just dropped. {title}.",
        f"Big news from {source} that's going to blow your mind. {title}.",
        f"This changes everything for gamers. {title}.",
        f"Gamers, this one is huge. {title}.",
        f"Wait until you hear this gaming news. {title}.",
        f"This is the biggest gaming story today. {title}.",
    ]
    return random.choice(hooks)


def main():
    parser = argparse.ArgumentParser(description="Gaming News Video Bot")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--video", default=None)
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="public")
    parser.add_argument("--output", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--shorts", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("  GAMING NEWS VIDEO BOT")
    print("=" * 60)

    if args.video:
        video_path = args.video
        if not os.path.exists(video_path):
            print(f"[!] Video not found: {video_path}")
            sys.exit(1)
        file_size = os.path.getsize(video_path) / (1024 * 1024)
        print(f"\n    Using existing video: {video_path} ({file_size:.1f} MB)")
        news = fetch_gaming_news() or []
        args.upload = True
    else:
        print("\n[1/3] Fetching latest gaming news...")
        news = fetch_gaming_news()
        if not news:
            print("[!] No news found. Aborting.")
            sys.exit(1)

        print(f"    Found {len(news)} stories:")
        for i, item in enumerate(news, 1):
            print(f"    {i}. {item['title'][:90]}")

        hook = get_hook(news)
        script = gaming_news_to_script(news, hook=hook)
        print(f"\n    Script generated ({len(script)} chars)")
        print(f"    Hook: {hook}")

        if args.dry_run:
            print("\n" + "=" * 60)
            print("  SCRIPT PREVIEW (dry-run)")
            print("=" * 60)
            print(script)
            print("=" * 60)
            return

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = args.output or os.path.join(
            os.path.dirname(__file__), f"Gaming_News_{ts}.mp4",
        )

        print(f"\n[2/3] Creating HD video...")
        video_path = create_gaming_video(news, script, output_path)
        file_size = os.path.getsize(video_path) / (1024 * 1024)
        print(f"    Video saved: {video_path} ({file_size:.1f} MB)")

        if args.shorts:
            shorts_path = os.path.join(
                os.path.dirname(__file__), f"Shorts_{ts}.mp4",
            )
            print(f"\n[2b/3] Creating YouTube Short...")
            create_shorts(news, script, shorts_path)
            shorts_size = os.path.getsize(shorts_path) / (1024 * 1024)
            print(f"    Short saved: {shorts_path} ({shorts_size:.1f} MB)")

    if args.upload:
        print(f"\n[3/3] Uploading to YouTube...")
        from youtube_uploader import upload_video, upload_thumbnail

        title = _generate_title(news)
        description = generate_description(news)
        tags = [
            "Gaming News", "Video Games", "PlayStation", "Xbox", "Nintendo",
            "PC Gaming", "Game News", "Gaming Update", "Esports", "Game Launch",
            "Console", "PS5", "Xbox Series X", "Nintendo Switch", "Steam",
            "Gaming Community", "Game Reveal", "Gaming 2026", "Gaming Videos",
            "GameTrailers",
        ]

        video_id = upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            privacy_status=args.privacy,
        )

        if video_id:
            print(f"\n[SUCCESS] Published at: https://youtu.be/{video_id}")
            thumb_path = generate_thumbnail(news[0]["title"] if news else "Gaming News")
            upload_thumbnail(video_id, thumb_path)

            if args.shorts and os.path.exists(shorts_path):
                shorts_id = upload_video(
                    video_path=shorts_path,
                    title=f"{title} #Shorts",
                    description=description + "\n\n#Shorts #YouTubeShorts #GamingShorts",
                    tags=tags + ["Shorts", "YouTubeShorts", "GamingShorts"],
                    privacy_status=args.privacy,
                )
                if shorts_id:
                    print(f"    Shorts: https://youtu.be/{shorts_id}")
                    thumb_path = generate_thumbnail(news[0]["title"] if news else "Gaming News")
                    upload_thumbnail(shorts_id, thumb_path)
        else:
            print("\n Upload skipped or failed.")
    else:
        print(f"\n[3/3] Skipped upload (use --upload flag)")
        print(f"    Preview: {video_path}")

    print("\n[DONE]")


if __name__ == "__main__":
    main()
