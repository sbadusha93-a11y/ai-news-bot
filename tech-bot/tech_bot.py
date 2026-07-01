#!/usr/bin/env python3

import os
import sys
import argparse
import random
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

from tech_content import generate_content, SCRIPT_FORMATS
from tech_tips import get_random_tips, generate_short_script, CTAS
from video_maker import create_tech_video, create_longform_video, create_tech_short
from thumbnail_maker import generate_thumbnail


def _generate_title(content):
    return content["title"]


def _format_label(fmt):
    labels = {
        "tutorial": "TUTORIAL", "comparison": "COMPARISON", "case_study": "CASE STUDY",
        "tech_list": "TOP 10 LIST", "tech_facts": "TECH FACTS",
    }
    return labels.get(fmt, fmt.upper())


def generate_description(content):
    fmt = content["format"]
    title = content["title"]
    label = _format_label(fmt)
    lines = [f"{label}: {title}", ""]
    descs = {
        "tutorial": "Step-by-step tutorial showing you exactly how to use AI tools to get real results.",
        "comparison": "Honest comparison of the top AI tools tested side by side so you can choose the right one.",
        "case_study": "Real experiment with real results. I tested AI so you know what actually works.",
        "tech_list": "The ultimate list of the best tech tools, gadgets, and knowledge you need.",
        "tech_facts": "Mind-blowing technology facts that will change how you see the world.",
    }
    lines.append(descs.get(fmt, "Tech content that helps you work smarter."))
    lines.append("")
    lines.append("In this video:")
    for seg in content["segments"]:
        t = seg.get("title") or seg.get("heading") or ""
        if t:
            st = seg.get("step_num")
            prefix = f"Step {st}: " if st else ""
            lines.append(f"{prefix}{t}")
    lines.append("")
    lines.append("Questions? Drop them in the comments.")
    lines.append("Subscribe for more tech tutorials and comparisons.")
    lines.append("")
    lines.append(datetime.now().strftime("%B %d, %Y"))
    lines.append("")
    tags_str = "#Tech #AI #Tutorial #Productivity #Automation #ArtificialIntelligence #TechTools #HowTo #Comparison #Review"
    lines.append(tags_str)
    return "\n".join(lines)


def get_tags(content):
    tags = content.get("tags", [])
    base = [
        "Tech", "Technology", "AI", "Artificial Intelligence", "Productivity",
        "Tech Tools", "Tutorial", "How To", "Automation",
    ]
    return list(dict.fromkeys(tags + base))


def main():
    parser = argparse.ArgumentParser(description="Tech Content Video Bot")
    parser.add_argument("--format", choices=["random", "tech_list", "tech_facts", "tutorial", "comparison", "case_study"],
                        default="random", help="Content format (default: random)")
    parser.add_argument("--shorts", type=int, default=0,
                        help="Generate N YouTube Shorts from tech tips pool (default: 0)")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--video", default=None)
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="public")
    parser.add_argument("--output", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("  TECH CONTENT STUDIO")
    print("=" * 60)

    if args.shorts > 0:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        tips = get_random_tips(args.shorts)
        for i, tip in enumerate(tips):
            tip["cta"] = random.choice(CTAS) if not tip.get("cta") else tip["cta"]
            print(f"\n[{i+1}/{args.shorts}] Generating Short...")
            print(f"    Tip: {tip['hook'][:70]}...")
            if args.dry_run:
                print(f"    Script: {generate_short_script(tip)}")
                continue
            output_path = args.output or os.path.join(
                os.path.dirname(__file__), f"Short_{ts}_{i+1}.mp4",
            )
            path = create_tech_short(tip, output_path)
            size = os.path.getsize(path) / (1024 * 1024)
            print(f"    Saved: {path} ({size:.1f} MB)")
        print(f"\n[DONE] Generated {args.shorts} Short(s)")
        return

    if args.video:
        video_path = args.video
        if not os.path.exists(video_path):
            print(f"[!] Video not found: {video_path}")
            sys.exit(1)
        file_size = os.path.getsize(video_path) / (1024 * 1024)
        print(f"\n    Using existing video: {video_path} ({file_size:.1f} MB)")
        content = generate_content(format="tech_list")
        args.upload = True
    else:
        print("\n[1/3] Generating content...")
        content = generate_content(format=args.format)
        fmt = content["format"]
        print(f"    Format: {fmt.upper()}")
        print(f"    Title: {content['title']}")
        print(f"    Segments: {len(content['segments'])}")
        print(f"    Script: {len(content['script'])} chars")

        if args.dry_run:
            print("\n" + "=" * 60)
            print("  SCRIPT PREVIEW")
            print("=" * 60)
            print(content["script"])
            print("=" * 60)
            return

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = args.output or os.path.join(
            os.path.dirname(__file__), f"Tech_{fmt}_{ts}.mp4",
        )

        print(f"\n[2/3] Creating HD video...")
        if content["format"] in SCRIPT_FORMATS:
            video_path = create_longform_video(content, output_path)
        else:
            video_path = create_tech_video(content, output_path)
        file_size = os.path.getsize(video_path) / (1024 * 1024)
        print(f"    Video saved: {video_path} ({file_size:.1f} MB)")

    if args.upload:
        print(f"\n[3/3] Uploading to YouTube...")
        from youtube_uploader import upload_video, upload_thumbnail
        title = _generate_title(content)
        description = generate_description(content)
        tags = get_tags(content)
        video_id = upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            privacy_status=args.privacy,
        )
        if video_id:
            print(f"\n[SUCCESS] Published at: https://youtu.be/{video_id}")
            thumb_path = generate_thumbnail(content["title"])
            upload_thumbnail(video_id, thumb_path)
        else:
            print("\n Upload skipped or failed.")
    else:
        print(f"\n[3/3] Skipped upload (use --upload flag)")
        print(f"    Preview: {video_path}")

    print("\n[DONE]")


if __name__ == "__main__":
    main()
