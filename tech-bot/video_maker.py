import os
import re
import random
import requests
import asyncio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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


def create_text_image(text, size=(1280, 720), bg_color=(5, 10, 40)):
    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)
    accent_color = (0, 140, 255)

    try:
        title_font = ImageFont.truetype("arial.ttf", 64)
        body_font = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    lines = text.split("\n")
    title = lines[0] if lines else ""
    body = "\n".join(lines[1:]) if len(lines) > 1 else ""

    if title:
        _, _, tw, th = draw.textbbox((0, 0), title, font=title_font)
        tx = (size[0] - tw) // 2
        ty = 80
        draw.text((tx - 3, ty - 3), title, font=title_font, fill=(0, 0, 0))
        draw.text((tx + 3, ty + 3), title, font=title_font, fill=(0, 0, 0))
        draw.text((tx, ty), title, font=title_font, fill=accent_color)

    if body:
        wrapped = _get_text_dimensions(body, body_font, size[0] - 200)
        line_height = body_font.getbbox("Ag")[3] - body_font.getbbox("Ag")[1] + 10
        y_start = ty + th + 60 if title else 80
        for i, line in enumerate(wrapped[:20]):
            _, _, lw, _ = draw.textbbox((0, 0), line, font=body_font)
            lx = (size[0] - lw) // 2
            draw.text((lx, y_start + i * line_height), line, font=body_font, fill=(200, 210, 240))

    img_path = os.path.join(os.path.dirname(__file__), "assets", "temp_title.png")
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    img.save(img_path)
    return img_path


def _build_pexels_query(title, summary=""):
    text = (title + " " + summary).lower()
    if not _is_safe_query(text):
        return "technology abstract digital wallpaper"

    brand_map = {
        "apple": "MacBook Apple", "iphone": "iPhone smartphone",
        "google": "Google technology", "android": "smartphone Android",
        "samsung": "Samsung Galaxy", "microsoft": "Microsoft technology",
        "windows": "Windows computer", "mac": "MacBook laptop",
        "chatgpt": "artificial intelligence", "openai": "AI artificial intelligence",
        "ai": "artificial intelligence", "chatbot": "AI chat technology",
        "robot": "robot technology", "tesla": "electric car technology",
    }
    for brand, term in brand_map.items():
        if brand in text:
            return term

    tech_terms = ["technology", "computer", "laptop", "digital", "cyber", "innovation", "abstract tech"]
    words = re.findall(r"[a-zA-Z]{4,}", text)
    stopwords = {"the", "this", "that", "with", "from", "have", "been", "were",
                 "what", "when", "where", "which", "their", "they", "your", "will",
                 "would", "could", "should", "after", "before", "between", "about",
                 "tool", "apps", "app", "new", "best", "top", "list"}
    for w in words:
        lw = w.lower()
        if len(lw) > 4 and lw not in stopwords and lw not in ADULT_IMAGE_TERMS:
            tech_terms.append(lw)
            if len(tech_terms) >= 4:
                break

    return " ".join(tech_terms[:3]) + " technology"


def _download_pexels_image(keywords, output_path, title=""):
    api_key = os.getenv("PEXELS_API_KEY", "")
    if not api_key:
        return None

    query = _build_pexels_query(title, " ".join(keywords)) if title else "technology"
    if not _is_safe_query(query):
        query = "technology digital abstract"

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
        {"bg": ((5, 10, 40), (10, 30, 80)), "accent": (0, 120, 255), "glow": (80, 180, 255)},
        {"bg": ((40, 5, 50), (80, 10, 100)), "accent": (180, 50, 255), "glow": (200, 120, 255)},
        {"bg": ((10, 20, 10), (20, 50, 20)), "accent": (0, 200, 100), "glow": (80, 255, 150)},
        {"bg": ((50, 10, 10), (100, 20, 20)), "accent": (255, 80, 50), "glow": (255, 150, 100)},
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
    clip = ImageClip(img_path, duration=duration)
    clip = clip.resized(width=W)
    if clip.h < H:
        clip = clip.resized(height=H)
    clip = clip.cropped(x1=0, y1=0, x2=W, y2=H)
    return clip.with_duration(duration)


def create_tech_video(content, output_path="tech_video.mp4"):
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

    os.makedirs(os.path.join(os.path.dirname(__file__), "assets"), exist_ok=True)

    print("[+] Generating voiceover with neural TTS...")
    audio_path = os.path.join(os.path.dirname(__file__), "assets", "narration.mp3")
    _generate_narration(content["script"], audio_path)
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    print(f"[+] Audio duration: {audio_duration:.1f}s")

    segments = content["segments"]
    item_segments = [s for s in segments if s["type"] == "item"]
    intro_segments = [s for s in segments if s["type"] == "intro"]
    outro_segments = [s for s in segments if s["type"] == "outro"]
    narrated_count = len(intro_segments) + len(item_segments) + len(outro_segments)
    segment_duration = audio_duration / narrated_count if narrated_count > 0 else audio_duration
    cta_duration = 6

    W, H = 1280, 720
    video_segments = []
    accent = (0, 180, 255)

    for segment in segments:
        seg_type = segment["type"]
        current_dur = segment_duration

        if seg_type == "intro":
            print("    Intro...")
            display = segment["text"]
        elif seg_type == "item":
            number = segment.get("number", "")
            title = segment["title"]
            display = f"#{number}  {title}" if number else title
        elif seg_type == "outro":
            print("    Outro...")
            display = "Thanks for watching!"
        else:
            display = segment.get("text", "")

        img_path = _create_segment_image(display, (W, H), (5, 10, 40), accent, 36)
        clip = ImageClip(img_path, duration=current_dur)
        video_segments.append(clip)

    print("    End card...")
    cta_img = _create_segment_image(
        "Thanks for watching!\n\nLIKE if you learned something new\nCOMMENT your thoughts\nSUBSCRIBE for more tech content",
        (W, H), (5, 10, 40), (0, 191, 255), 40
    )
    cta_clip = ImageClip(cta_img, duration=cta_duration)
    video_segments.append(cta_clip)

    print("[+] Concatenating video...")
    final_video = concatenate_videoclips(video_segments, method="compose")
    total_duration = audio_duration + cta_duration
    final_video = final_video.with_duration(total_duration)

    from moviepy import AudioClip as AC
    silence = AC(lambda t: 0, duration=7, fps=22050)
    silence_audio = silence.with_duration(cta_duration)
    final_video = final_video.with_audio(concatenate_audioclips([audio, silence_audio]))

    print(f"[+] Writing video to {output_path}...")
    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=15,
        preset="ultrafast",
        threads=4,
    )

    final_video.close()
    audio.close()
    return output_path


def _download_shorts_images(category="technology", count=1):
    output_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
    os.makedirs(output_dir, exist_ok=True)
    api_key = os.getenv("PEXELS_API_KEY", "")
    img_paths = []
    for i in range(count):
        fpath = os.path.join(output_dir, f"short_{i}.jpg")
        if api_key:
            try:
                resp = requests.get(
                    "https://api.pexels.com/v1/search",
                    headers={"Authorization": api_key},
                    params={"query": category, "per_page": 5, "orientation": "portrait", "size": "large"},
                    timeout=15,
                )
                if resp.status_code == 200:
                    photos = resp.json().get("photos", [])
                    for photo in photos:
                        url_lower = photo["url"].lower() if "url" in photo else ""
                        alt_lower = photo.get("alt", "").lower()
                        if not _is_safe_query(url_lower + " " + alt_lower):
                            continue
                        img_url = photo["src"]["large2x"]
                        img_resp = requests.get(img_url, timeout=20)
                        if img_resp.status_code == 200:
                            with open(fpath, "wb") as f:
                                f.write(img_resp.content)
                            img_paths.append(fpath)
                            break
            except Exception:
                pass
    return img_paths


def _create_gradient_overlay(size=(1080, 1920)):
    from PIL import Image as PILImage, ImageDraw as PILDraw
    W, H = size
    overlay = PILImage.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = PILDraw.Draw(overlay)
    for y in range(H):
        a = int(80 + 120 * (y / H))
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    path = os.path.join(os.path.dirname(__file__), "assets", "overlay.png")
    overlay.save(path)
    return path


def create_tech_short(tip_data, output_path="tech_short.mp4"):
    from moviepy import (
        ImageClip, AudioFileClip, TextClip,
        CompositeVideoClip, concatenate_audioclips,
    )
    os.makedirs(os.path.join(os.path.dirname(__file__), "assets"), exist_ok=True)

    script = f"{tip_data['hook']} {tip_data['content']} {tip_data['cta']}"
    print("[+] Generating Short voiceover with neural TTS...")
    audio_path = os.path.join(os.path.dirname(__file__), "assets", "short_narration.mp3")
    _generate_narration(script, audio_path)
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    W, H = 1080, 1920

    print("[+] Downloading background image...")
    category = tip_data.get("category", "technology")
    img_paths = _download_shorts_images(category)
    if img_paths and os.path.exists(img_paths[0]):
        bg = _ken_burns_clip(img_paths[0], audio_duration, (W, H))
    else:
        bg = ImageClip(
            np.array(Image.new("RGB", (W, H), (5, 10, 40))),
            duration=audio_duration,
        )

    overlay_path = _create_gradient_overlay((W, H))
    overlay = ImageClip(
        np.array(Image.open(overlay_path).convert("RGBA")),
        duration=audio_duration,
        is_mask=True,
    ).with_position(0, 0)

    hook = tip_data["hook"]
    content = tip_data["content"]
    cta = tip_data["cta"]
    total_chars = len(hook) + len(content) + len(cta) + 2
    hook_end = (len(hook) / total_chars) * audio_duration
    content_end = ((len(hook) + len(content) + 1) / total_chars) * audio_duration

    hook_clip = TextClip(
        text=hook,
        font_size=56, color="white", font=_get_font_path(),
        stroke_color="black", stroke_width=3, method="caption",
        size=(W - 120, None),
    ).with_start(0).with_duration(hook_end).with_position(("center", H * 0.30))

    content_clip = TextClip(
        text=content,
        font_size=38, color="white", font=_get_font_path(),
        stroke_color="black", stroke_width=2, method="caption",
        size=(W - 120, None),
    ).with_start(hook_end).with_duration(content_end - hook_end).with_position(("center", H * 0.30))

    cta_clip = TextClip(
        text=cta,
        font_size=34, color="#00BFFF", font=_get_font_path(),
        stroke_color="black", stroke_width=2, method="caption",
        size=(W - 120, None),
    ).with_start(content_end).with_duration(audio_duration - content_end).with_position(("center", H * 0.75))

    brand_bar = ImageClip(
        np.array(Image.new("RGB", (W, 50), (0, 120, 255))),
        duration=audio_duration,
    ).with_position(("center", H - 50))

    brand_text = TextClip(
        text="TECH INSIDER",
        font_size=24, color="white", font=_get_font_path(),
    ).with_start(0).with_duration(audio_duration).with_position(("center", H - 44))

    final = CompositeVideoClip([
        bg, overlay, hook_clip, content_clip, cta_clip,
        brand_bar, brand_text,
    ], size=(W, H)).with_duration(audio_duration).with_audio(audio)

    print(f"[+] Writing Short to {output_path} ({audio_duration:.1f}s)...")
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=30,
        bitrate="8000k",
        preset="medium",
        threads=4,
    )

    final.close()
    audio.close()
    return output_path


def _get_segment_duration(segments, audio_duration):
    total_chars = sum(len(s.get("text", "") or "") for s in segments)
    if total_chars == 0:
        return audio_duration / max(len(segments), 1)
    for seg in segments:
        seg["_dur"] = (len(seg.get("text", "") or "") / total_chars) * audio_duration
    return segments


def _download_segment_images(segments):
    for seg in segments:
        query = seg.get("img", "technology")
        paths = _download_images([query], count=1, title=query)
        seg["_img"] = paths[0] if paths else None


def _create_segment_image(text, size=(1280, 720), bg_color=(5, 10, 40), accent_color=(0, 140, 255), font_size=32):
    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(_get_font_path(), font_size)
        title_font = ImageFont.truetype(_get_font_path(), min(font_size + 14, 64))
    except Exception:
        font = ImageFont.load_default()
        title_font = font

    lines = text.split("\n")
    title = lines[0] if lines else ""
    body = "\n".join(lines[1:]) if len(lines) > 1 else ""

    if title:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (size[0] - tw) // 2
        ty = 60
        draw.text((tx + 2, ty + 2), title, font=title_font, fill=(0, 0, 0))
        draw.text((tx, ty), title, font=title_font, fill=accent_color)

    if body:
        wrapped = _get_text_dimensions(body, font, size[0] - 160)
        line_height = font_size + 10
        y_start = ty + 80 if title else 60
        for i, line in enumerate(wrapped[:18]):
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            lx = (size[0] - lw) // 2
            draw.text((lx + 1, y_start + i * line_height + 1), line, font=font, fill=(0, 0, 0))
            draw.text((lx, y_start + i * line_height), line, font=font, fill=(220, 225, 240))

    bar_y = size[1] - 60
    draw.rectangle([(40, bar_y), (size[0] - 40, bar_y + 3)], fill=accent_color)

    temp_path = os.path.join(os.path.dirname(__file__), "assets", f"seg_{hash(text) & 0xFFFF:04x}.png")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    img.save(temp_path)
    return temp_path


def create_longform_video(content, output_path="tech_video.mp4"):
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
    os.makedirs(os.path.join(os.path.dirname(__file__), "assets"), exist_ok=True)

    print("[+] Generating voiceover with neural TTS...")
    audio_path = os.path.join(os.path.dirname(__file__), "assets", "narration.mp3")
    _generate_narration(content["script"], audio_path)
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration
    print(f"[+] Audio duration: {audio_duration:.1f}s ({audio_duration/60:.1f} min)")

    W, H = 1280, 720
    segments = content["segments"]
    segments = _get_segment_duration(segments, audio_duration)

    video_segments = []
    accent = (0, 180, 255)

    for seg in segments:
        seg_type = seg["type"]
        dur = seg["_dur"]

        if seg_type == "intro":
            display = seg.get("text", "")
        elif seg_type == "step":
            num = seg.get("step_num", 1)
            title = seg.get("title", "")
            display = f"STEP {num}\n{title}"
        elif seg_type == "comparison":
            heading = seg.get("heading", "")
            display = f"COMPARISON\n{heading}"
        elif seg_type == "result":
            title = seg.get("title", "Results")
            display = f"RESULTS\n{title}"
        else:
            display = seg.get("text", "")

        img_path = _create_segment_image(display, (W, H), (5, 10, 40), accent, 36)
        clip = ImageClip(img_path, duration=dur)
        video_segments.append(clip)

    print("    End card...")
    cta_img = _create_segment_image(
        "Thanks for watching!\n\nLIKE if you learned something\nCOMMENT your questions\nSUBSCRIBE for more tutorials",
        (W, H), (5, 10, 40), (0, 191, 255), 40
    )
    cta_clip = ImageClip(cta_img, duration=6)
    video_segments.append(cta_clip)

    print(f"[+] Concatenating {len(video_segments)} segments...")
    final_video = concatenate_videoclips(video_segments, method="compose")
    total_duration = audio_duration + 6
    final_video = final_video.with_duration(total_duration)

    from moviepy import AudioClip as AC
    silence = AC(lambda t: 0, duration=7, fps=22050)
    silence_audio = silence.with_duration(6)
    final_video = final_video.with_audio(concatenate_audioclips([audio, silence_audio]))

    print(f"[+] Writing video to {output_path}...")
    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=15,
        preset="ultrafast",
        threads=4,
    )

    final_video.close()
    audio.close()
    return output_path
