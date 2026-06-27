import os
import re
import random
import requests
import asyncio
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ADULT_IMAGE_TERMS = {
    "sex", "porn", "nude", "naked", "erotic", "xxx", "nsfw", "hentai",
    "onlyfans", "escort", "milf", "boobs", "lewd", "horny", "slut",
    "bdsm", "fetish", "masturbat", "penis", "vagina", "nipple",
    "bikini", "lingerie", "swimsuit", "underwear", "sexy", "adult",
}


def _is_safe_query(query):
    lowered = query.lower()
    for term in ADULT_IMAGE_TERMS:
        if term in lowered:
            return False
    return True


def _find_ffmpeg():
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        os.environ["IMAGEIO_FFMPEG_EXE"] = exe
        return exe
    except Exception:
        import shutil
        exe = shutil.which("ffmpeg")
        if exe:
            os.environ["IMAGEIO_FFMPEG_EXE"] = exe
            return exe
        return "ffmpeg"


_ffmpeg_path = _find_ffmpeg()


def _generate_narration(script, output_path):
    try:
        import edge_tts
        voice = random.choice([
            "en-US-JennyNeural", "en-US-AriaNeural",
            "en-GB-SoniaNeural", "en-GB-RyanNeural",
            "en-US-GuyNeural", "en-US-ChristopherNeural",
        ])
        async def _do_tts():
            communicate = edge_tts.Communicate(script, voice)
            await communicate.save(output_path)
        asyncio.run(_do_tts())
        print(f"    Voice: {voice}")
        return True
    except Exception:
        from gtts import gTTS
        tts = gTTS(text=script, lang="en", slow=False)
        tts.save(output_path)
        return True


def _get_text_dimensions(text, font, max_width):
    lines = []
    words = text.split()
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = font.getbbox(test)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def create_text_image(text, size=(1280, 720), bg_color=(10, 10, 35)):
    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)
    accent_color = (0, 200, 80)

    try:
        title_font = ImageFont.truetype("arial.ttf", 64)
        body_font = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    lines = text.split("\n")
    title = lines[0] if lines else "Gaming News"
    body = "\n".join(lines[1:]) if len(lines) > 1 else ""

    _, _, tw, th = draw.textbbox((0, 0), title, font=title_font)
    tx = (size[0] - tw) // 2
    ty = 80
    draw.text((tx - 3, ty - 3), title, font=title_font, fill=(0, 0, 0))
    draw.text((tx + 3, ty + 3), title, font=title_font, fill=(0, 0, 0))
    draw.text((tx, ty), title, font=title_font, fill=accent_color)

    if body:
        wrapped = _get_text_dimensions(body, body_font, size[0] - 200)
        line_height = body_font.getbbox("Ag")[3] - body_font.getbbox("Ag")[1] + 10
        y_start = ty + th + 60
        for i, line in enumerate(wrapped[:20]):
            _, _, lw, _ = draw.textbbox((0, 0), line, font=body_font)
            lx = (size[0] - lw) // 2
            draw.text((lx, y_start + i * line_height), line, font=body_font, fill=(220, 220, 240))

    img_path = os.path.join(os.path.dirname(__file__), "assets", "temp_title.png")
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    img.save(img_path)
    return img_path


def _build_pexels_query(title, summary=""):
    text = (title + " " + summary).lower()
    if not _is_safe_query(text):
        return "gaming video game console controller wallpaper"

    brand_map = {
        "playstation": "PlayStation console", "ps5": "PlayStation controller",
        "xbox": "Xbox console", "nintendo": "Nintendo Switch",
        "pc": "gaming PC setup", "steam": "Steam gaming",
        "rockstar": "GTA video game", "ubisoft": "gaming wallpaper",
        "ea": "video game", "epic": "gaming",
    }
    for brand, term in brand_map.items():
        if brand in text:
            return term

    game_terms = ["gaming", "video game", "game controller", "gaming setup", "console", "esports"]
    words = re.findall(r"[a-zA-Z]{4,}", text)
    stopwords = {"the", "this", "that", "with", "from", "have", "been", "were",
                 "what", "when", "where", "which", "their", "they", "your", "will",
                 "would", "could", "should", "after", "before", "between", "about",
                 "game", "games", "gaming", "new", "news", "announced", "release"}
    for w in words:
        lw = w.lower()
        if len(lw) > 4 and lw not in stopwords and lw not in ADULT_IMAGE_TERMS:
            game_terms.append(w)
            if len(game_terms) >= 4:
                break

    return " ".join(game_terms[:3]) + " gaming wallpaper"


def _download_pexels_image(keywords, output_path, title=""):
    api_key = os.getenv("PEXELS_API_KEY", "")
    if not api_key:
        return None

    query = _build_pexels_query(title, " ".join(keywords)) if title else "gaming wallpaper"
    if not _is_safe_query(query):
        query = "gaming video game wallpaper"

    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 5, "orientation": "landscape", "size": "large"},
            timeout=15,
        )
        if resp.status_code == 200:
            photos = resp.json().get("photos", [])
            if photos:
                for photo in photos:
                    url_lower = photo["url"].lower() if "url" in photo else ""
                    alt_lower = photo.get("alt", "").lower()
                    combined = url_lower + " " + alt_lower
                    if not _is_safe_query(combined):
                        continue
                    img_url = photo["src"]["large2x"]
                    img_resp = requests.get(img_url, timeout=20)
                    if img_resp.status_code == 200:
                        with open(output_path, "wb") as f:
                            f.write(img_resp.content)
                        return output_path
    except Exception:
        pass
    return None


def _generate_art_bg(count=3, output_size=(1280, 720)):
    W, H = output_size
    output_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    palette = [
        {"bg": ((10, 40, 10), (20, 100, 50)), "accent": (0, 255, 100), "glow": (100, 255, 150)},
        {"bg": ((40, 10, 40), (100, 20, 90)), "accent": (255, 50, 180), "glow": (255, 150, 220)},
        {"bg": ((10, 10, 50), (20, 30, 120)), "accent": (60, 140, 255), "glow": (150, 200, 255)},
        {"bg": ((50, 20, 10), (120, 40, 20)), "accent": (255, 100, 50), "glow": (255, 180, 100)},
    ]

    for i in range(count):
        scheme = random.choice(palette)
        (r1, g1, b1), (r2, g2, b2) = scheme["bg"]
        accent = scheme["accent"]

        img = Image.new("RGB", (W, H), (r1, g1, b1))
        draw = ImageDraw.Draw(img)

        for y in range(H):
            blend = y / H
            cr = int(r1 + (r2 - r1) * blend)
            cg = int(g1 + (g2 - g1) * blend)
            cb = int(b1 + (b2 - b1) * blend)
            draw.line([(0, y), (W, y)], fill=(cr, cg, cb))

        for _ in range(5):
            x = random.randint(0, W)
            y = random.randint(0, H)
            size = random.randint(20, 60)
            color = tuple(max(0, min(255, c + random.randint(-40, 40))) for c in accent)
            draw.ellipse([x - size // 2, y - size // 2, x + size // 2, y + size // 2],
                         fill=color, outline=None)

        for _ in range(random.randint(3, 6)):
            x1 = random.randint(0, W)
            y1 = random.randint(0, H)
            x2 = x1 + random.randint(-250, 250)
            y2 = y1 + random.randint(-250, 250)
            color = tuple(max(0, min(255, c + random.randint(-30, 30))) for c in accent)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=random.randint(1, 4))

        fpath = os.path.join(output_dir, f"bg_{i}.jpg")
        img.save(fpath, quality=92)
        paths.append(fpath)
    return paths


def _download_images(keywords, count=3, title=""):
    output_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
    os.makedirs(output_dir, exist_ok=True)
    img_paths = []

    for i in range(count):
        fpath = os.path.join(output_dir, f"photo_{i}.jpg")
        path = _download_pexels_image(keywords, fpath, title=title)
        if path is None:
            path = _generate_art_bg(count=1, output_size=(1280, 720))
            if path:
                path = path[0]
        if path:
            img_paths.append(path)

    return img_paths[:count]


def _get_font_path():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "DejaVuSans"


def _ken_burns_clip(img_path, duration, output_size=(1280, 720)):
    from moviepy import ImageClip

    W, H = output_size
    PAN_SCALE = 1.15

    clip = ImageClip(img_path, duration=duration)
    clip = clip.resized(width=int(W * PAN_SCALE))
    if clip.h < int(H * PAN_SCALE):
        clip = clip.resized(height=int(H * PAN_SCALE))

    max_dx = clip.w - W
    max_dy = clip.h - H

    direction = random.choice([
        (0.4, 0.3), (0.3, 0.4), (0.5, 0.2), (0.2, 0.5), (0.5, 0.5),
    ])

    start_x = max_dx * direction[0]
    start_y = max_dy * direction[1]
    end_x = max_dx * (1 - direction[0])
    end_y = max_dy * (1 - direction[1])

    def pos_func(t):
        progress = t / duration if duration > 0 else 0
        x = start_x + (end_x - start_x) * progress
        y = start_y + (end_y - start_y) * progress
        return (-x, -y)

    return clip.with_position(pos_func).with_duration(duration)


def create_gaming_video(news_items, script, output_path="gaming_news_video.mp4"):
    from moviepy import (
        ImageClip, AudioFileClip, TextClip,
        CompositeVideoClip, concatenate_videoclips, concatenate_audioclips,
    )

    os.makedirs(os.path.join(os.path.dirname(__file__), "assets"), exist_ok=True)

    print("[+] Generating voiceover with neural TTS...")
    audio_path = os.path.join(os.path.dirname(__file__), "assets", "narration.mp3")
    _generate_narration(script, audio_path)
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    print(f"[+] Audio duration: {audio_duration:.1f}s")
    print("[+] Creating video segments...")

    segments = []
    segment_duration = audio_duration / (len(news_items) + 1)
    W, H = 1280, 720

    print("    Intro...")
    intro_img_path = _download_images(["gaming", "controller", "console"], count=1, title="Gaming News")
    if intro_img_path:
        intro_bg = _ken_burns_clip(intro_img_path[0], segment_duration, (W, H))
    else:
        intro_bg_img = create_text_image("GAMING NEWS\nTop Stories Today", bg_color=(10, 40, 10))
        intro_bg = ImageClip(intro_bg_img, duration=segment_duration).with_fps(24)

    intro_txt = TextClip(
        text="GAMING NEWS\nTop Stories Today",
        font_size=52, color="white", font=_get_font_path(),
        stroke_color="black", stroke_width=3, method="caption",
        size=(W - 100, None),
    ).with_duration(segment_duration).with_position("center").with_start(0)

    segments.append(CompositeVideoClip([intro_bg, intro_txt], size=(W, H)).with_duration(segment_duration))

    for i, item in enumerate(news_items):
        print(f"    Story {i+1}: {item['title'][:60]}...")
        img_paths = _download_images([], count=1, title=item["title"])

        if img_paths:
            bg = _ken_burns_clip(img_paths[0], segment_duration, (W, H))
        else:
            txt_img = create_text_image(item["title"], bg_color=(20, 20, 50))
            bg = ImageClip(txt_img, duration=segment_duration).with_fps(24)

        summary = item.get("summary", "")[:200]
        caption_text = f"{item['title']}\n{summary}"

        txt_clip = TextClip(
            text=caption_text,
            font_size=26, color="white", font=_get_font_path(),
            stroke_color="black", stroke_width=2, method="caption",
            size=(W - 80, None),
        ).with_duration(segment_duration).with_position(("center", 80)).with_start(0)

        source_tag = TextClip(
            text=f"Source: {item.get('source', 'Gaming News')}",
            font_size=16, color="gray", font=_get_font_path(),
            stroke_color="black", stroke_width=1,
        ).with_duration(segment_duration).with_position(("right", H - 40)).with_start(0)

        scene = CompositeVideoClip([bg, txt_clip, source_tag], size=(W, H)).with_duration(segment_duration)
        segments.append(scene)

    print("    End card...")
    cta_duration = 6
    cta_clip = ImageClip(
        np.array(Image.new("RGB", (W, H), (10, 10, 35))), duration=cta_duration
    )
    cta_text = TextClip(
        text="Thanks for watching!\n\n👍 LIKE if you enjoyed\n💬 COMMENT your thoughts\n🔔 SUBSCRIBE for more",
        font_size=42, color="white", font=_get_font_path(),
        stroke_color="black", stroke_width=3, method="caption",
        size=(W - 100, None),
    ).with_duration(cta_duration).with_position("center").with_start(0)
    cta_segment = CompositeVideoClip([cta_clip, cta_text], size=(W, H)).with_duration(cta_duration)
    segments.append(cta_segment)

    print("[+] Concatenating video...")
    final_video = concatenate_videoclips(segments, method="compose")

    total_duration = audio_duration + cta_duration
    final_video = final_video.with_duration(total_duration)

    silence_path = os.path.join(os.path.dirname(__file__), "assets", "silence.mp3")
    if not os.path.exists(silence_path):
        from moviepy import AudioClip as AC
        silence = AC(lambda t: 0, duration=cta_duration, fps=22050)
        silence.write_audiofile(silence_path, logger=None)
    silence_audio = AudioFileClip(silence_path)
    final_video = final_video.with_audio(concatenate_audioclips([audio, silence_audio]))
    final_video = final_video.resized(height=720)

    print(f"[+] Writing video to {output_path}...")
    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=30,
        bitrate="8000k",
        preset="medium",
        threads=4,
    )

    final_video.close()
    audio.close()
    return output_path


def create_shorts(news_items, script, output_path="gaming_shorts.mp4"):
    from moviepy import (
        ImageClip, AudioFileClip, TextClip,
        CompositeVideoClip, concatenate_videoclips,
    )

    os.makedirs(os.path.join(os.path.dirname(__file__), "assets"), exist_ok=True)

    print("[+] Generating Shorts voiceover with neural TTS...")
    short_script = script[:800]
    audio_path = os.path.join(os.path.dirname(__file__), "assets", "shorts_narration.mp3")
    _generate_narration(short_script, audio_path)
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    W, H = 1080, 1920
    segments = []
    seg_dur = audio_duration / max(len(news_items) + 1, 1)

    print("    Intro...")
    intro_img_paths = _download_images(["gaming", "controller"], count=1, title="Gaming News")
    if intro_img_paths:
        intro_bg = _ken_burns_clip(intro_img_paths[0], seg_dur, (W, H))
    else:
        intro_bg = ImageClip(
            np.array(Image.new("RGB", (W, H), (10, 10, 35))), duration=seg_dur
        )
    txt_intro = TextClip(
        text="GAMING\nNEWS",
        font_size=80, color="white", font=_get_font_path(),
        stroke_color="black", stroke_width=3, method="caption",
        size=(W - 80, None),
    ).with_duration(seg_dur).with_position("center").with_start(0)
    segments.append(CompositeVideoClip([intro_bg, txt_intro]))

    for i, item in enumerate(news_items):
        print(f"    Story {i+1}...")
        img_paths = _download_images([], count=1, title=item["title"])

        if img_paths:
            bg_clip = _ken_burns_clip(img_paths[0], seg_dur, (W, H))
        else:
            bg_clip = ImageClip(
                np.array(Image.new("RGB", (H, W), (20, 20, 50))), duration=seg_dur
            )

        summary = item.get("summary", "")[:150]
        caption_text = f"{item['title']}\n{summary}"

        txt = TextClip(
            text=caption_text,
            font_size=32, color="white", font=_get_font_path(),
            stroke_color="black", stroke_width=2, method="caption",
            size=(W - 60, None),
        ).with_duration(seg_dur).with_position(("center", H - 500)).with_start(0)

        segments.append(CompositeVideoClip([bg_clip, txt], size=(W, H)))

    final = concatenate_videoclips(segments, method="compose")
    final = final.with_duration(audio_duration).with_audio(audio)

    print(f"[+] Writing Shorts to {output_path}...")
    final.write_videofile(
        output_path, codec="libx264", audio_codec="aac",
        fps=30, bitrate="8000k", preset="medium", threads=4,
    )
    final.close()
    audio.close()
    return output_path
