import os
import re
import random
import textwrap
import requests
import asyncio
from PIL import Image, ImageDraw, ImageFont
import numpy as np


BRAND_IMAGE_TERMS = {
    "samsung": "Samsung Galaxy smartphone product", "apple": "Apple iPhone product",
    "google": "Google Pixel phone", "xiaomi": "Xiaomi smartphone",
    "oneplus": "OnePlus phone", "sony": "Sony Xperia phone",
    "nokia": "Nokia phone", "motorola": "Motorola phone",
    "oppo": "Oppo smartphone", "vivo": "Vivo smartphone",
    "huawei": "Huawei phone", "honor": "Honor phone",
    "realme": "Realme phone", "nothing": "Nothing Phone",
    "asus": "Asus phone", "lenovo": "Lenovo phone",
}


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
            "en-US-JennyNeural",
            "en-US-AriaNeural",
            "en-GB-SoniaNeural",
            "en-GB-RyanNeural",
            "en-US-GuyNeural",
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

    accent_color = (0, 122, 255)

    try:
        title_font = ImageFont.truetype("arial.ttf", 64)
        body_font = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    lines = text.split("\n")
    title = lines[0] if lines else "News"
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

    for brand, term in BRAND_IMAGE_TERMS.items():
        if brand in text:
            return term

    keywords = ["smartphone", "technology", "mobile phone", "gadget"]
    words = re.findall(r"[a-zA-Z]{4,}", text)
    stopwords = {"the", "this", "that", "with", "from", "have", "been", "were",
                 "what", "when", "where", "which", "their", "they", "your", "will",
                 "would", "could", "should", "after", "before", "between", "about"}
    brand_names = {"samsung", "apple", "google", "xiaomi", "oneplus", "sony",
                   "nokia", "motorola", "oppo", "vivo", "huawei", "honor",
                   "realme", "asus", "lenovo"}
    for w in words:
        if w in brand_names:
            return f"{w} smartphone"
    for w in words:
        if len(w) > 4 and w.lower() not in stopwords:
            keywords.append(w)
            if len(keywords) >= 4:
                break

    return " ".join(keywords[:3]) + " smartphone technology"


def _download_pexels_image(keywords, output_path, title=""):
    api_key = os.getenv("PEXELS_API_KEY", "")
    if not api_key:
        return None

    query = _build_pexels_query(title, " ".join(keywords)) if title else " ".join(keywords[:3]) + " smartphone"
    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            timeout=15,
        )
        if resp.status_code == 200:
            photos = resp.json().get("photos", [])
            if photos:
                photo = random.choice(photos)
                img_url = photo["src"]["large2x"]
                img_resp = requests.get(img_url, timeout=20)
                if img_resp.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    return output_path
    except Exception:
        pass
    return None


def _generate_ai_art_bg(keywords, count=3, output_size=(1280, 720)):
    W, H = output_size
    output_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    palette = [
        {"bg": ((10, 10, 40), (20, 50, 100)), "accent": (0, 120, 255), "glow": (100, 180, 255)},
        {"bg": ((20, 5, 40), (60, 20, 90)), "accent": (180, 50, 255), "glow": (220, 150, 255)},
        {"bg": ((5, 20, 35), (10, 60, 80)), "accent": (0, 200, 150), "glow": (100, 255, 200)},
        {"bg": ((30, 10, 20), (80, 20, 50)), "accent": (255, 80, 80), "glow": (255, 150, 150)},
        {"bg": ((5, 15, 45), (15, 40, 100)), "accent": (60, 140, 255), "glow": (150, 200, 255)},
    ]

    for i in range(count):
        scheme = random.choice(palette)
        (r1, g1, b1), (r2, g2, b2) = scheme["bg"]
        accent = scheme["accent"]
        glow = scheme["glow"]

        img = Image.new("RGB", (W, H), (r1, g1, b1))
        draw = ImageDraw.Draw(img)

        for y in range(H):
            blend = y / H
            cr = int(r1 + (r2 - r1) * blend)
            cg = int(g1 + (g2 - g1) * blend)
            cb = int(b1 + (b2 - b1) * blend)
            draw.line([(0, y), (W, y)], fill=(cr, cg, cb))

        grid_size = random.randint(40, 80)
        for x in range(0, W, grid_size):
            for y in range(0, H, grid_size):
                if random.random() < 0.15:
                    color = (
                        random.randint(accent[0] - 30, accent[0] + 30),
                        random.randint(accent[1] - 30, accent[1] + 30),
                        random.randint(accent[2] - 30, accent[2] + 30),
                    )
                    color = tuple(max(0, min(255, c)) for c in color)
                    draw.rectangle([x, y, x + grid_size - 2, y + grid_size - 2],
                                   fill=color, outline=None)

        for _ in range(random.randint(3, 6)):
            cx = random.randint(50, W - 50)
            cy = random.randint(50, H - 50)
            r = random.randint(15, 40)
            for ring in range(r, 0, -3):
                color = tuple(
                    max(0, min(255, int(c + (glow[i] - c) * (1 - ring / r))))
                    for i, c in enumerate(accent)
                )
                draw.ellipse([cx - ring, cy - ring, cx + ring, cy + ring],
                             fill=color, outline=None)

        if random.random() < 0.6:
            line_count = random.randint(3, 8)
            for _ in range(line_count):
                x1 = random.randint(0, W)
                y1 = random.randint(0, H)
                x2 = x1 + random.randint(-200, 200)
                y2 = y1 + random.randint(-200, 200)
                line_color = (
                    random.randint(accent[0] - 20, accent[0] + 20),
                    random.randint(accent[1] - 20, accent[1] + 20),
                    random.randint(accent[2] - 20, accent[2] + 20),
                )
                line_color = tuple(max(0, min(255, c)) for c in line_color)
                draw.line([(x1, y1), (x2, y2)], fill=line_color, width=random.randint(1, 3))

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
            path = _generate_ai_art_bg(keywords, count=1, output_size=(1280, 720))
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
        r"C:\Windows\Fonts\consola.ttf",
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


def create_news_video(news_items, script, output_path="gadget_news_video.mp4"):
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
    intro_img_path = _download_images(["smartphone", "gadget", "technology"], count=1, title="Gadget News")
    if intro_img_path:
        intro_bg = _ken_burns_clip(intro_img_path[0], segment_duration, (W, H))
    else:
        intro_bg_img = create_text_image("Gadget News\nTop Stories Today", bg_color=(10, 10, 35))
        intro_bg = ImageClip(intro_bg_img, duration=segment_duration).with_fps(24)

    intro_txt = TextClip(
        text="GADGET NEWS\nTop Stories Today",
        font_size=48, color="white", font=_get_font_path(),
        stroke_color="black", stroke_width=3, method="caption",
        size=(W - 100, None),
    ).with_duration(segment_duration).with_position("center").with_start(0)

    segments.append(CompositeVideoClip([intro_bg, intro_txt], size=(W, H)).with_duration(segment_duration))

    for i, item in enumerate(news_items):
        print(f"    Story {i+1}: {item['title'][:60]}...")
        keywords = []
        img_paths = _download_images(keywords, count=1, title=item["title"])

        if img_paths:
            bg = _ken_burns_clip(img_paths[0], segment_duration, (W, H))
        else:
            txt_img = create_text_image(item["title"], bg_color=(20, 20, 50))
            bg = ImageClip(txt_img, duration=segment_duration).with_fps(24)

        summary = item.get("summary", "")[:200]
        caption_text = f"{item['title']}\n{summary}"

        txt_clip = TextClip(
            text=caption_text,
            font_size=26,
            color="white",
            stroke_color="black",
            stroke_width=2,
            font=_get_font_path(),
            method="caption",
            size=(W - 80, None),
        ).with_duration(segment_duration).with_position(("center", 80)).with_start(0)

        source_tag = TextClip(
            text=f"Source: {item.get('source', 'Tech News')}",
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
        from moviepy import AudioClip
        silence = AudioClip(lambda t: 0, duration=cta_duration, fps=22050)
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


def create_shorts(news_items, script, output_path="gadget_shorts.mp4"):
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
    intro_img_paths = _download_images(["smartphone", "gadget", "mobile"], count=1, title="Gadget News")
    if intro_img_paths:
        intro_bg = _ken_burns_clip(intro_img_paths[0], seg_dur, (W, H))
    else:
        intro_bg = ImageClip(
            np.array(Image.new("RGB", (W, H), (10, 10, 35))), duration=seg_dur
        )
    txt_intro = TextClip(
        text="GADGET\nNEWS",
        font_size=80, color="white", font=_get_font_path(),
        stroke_color="black", stroke_width=3, method="caption",
        size=(W - 80, None),
    ).with_duration(seg_dur).with_position("center").with_start(0)
    segments.append(CompositeVideoClip([intro_bg, txt_intro]))

    for i, item in enumerate(news_items):
        print(f"    Story {i+1}...")
        keywords = []
        img_paths = _download_images(keywords, count=1, title=item["title"])

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
