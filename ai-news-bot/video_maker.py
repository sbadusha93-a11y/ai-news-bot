import os
import re
import random
import textwrap
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import numpy as np


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
    title = lines[0] if lines else "AI News"
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


BLOCKED_KEYWORDS = {
    "sex", "sexy", "sexual", "porn", "porno", "pornography", "nude", "naked",
    "erotic", "adult", "xxx", "18+", "nsfw", "lingerie", "bikini", "swimsuit",
    "model", "models", "modeling", "fashion", "beauty", "makeup", "cosmetic",
    "girl", "girls", "boy", "boys", "child", "children", "baby", "babies",
    "kid", "kids", "teen", "teens", "teenager", "infant", "toddler",
    "woman", "women", "man", "men", "female", "male", "lady", "ladies",
    "gentleman", "gentlemen", "portrait", "people", "person", "human",
    "race", "racial", "ethnic", "ethnicity", "skin", "color", "colored",
    "black", "white", "asian", "african", "european", "american", "indian",
    "chinese", "japanese", "korean", "arab", "hispanic", "latino", "latinx",
    "caste", "religion", "religious", "muslim", "christian", "hindu", "jewish",
    "buddhist", "country", "countries", "nation", "national", "nationality",
    "patriotic", "flag", "border", "immigrant", "immigration",
    "discrimination", "inequality", "protest", "riot", "violence", "weapon",
    "war", "military", "soldier", "gun", "politics", "political", "politician",
    "election", "campaign", "vote", "voter", "government",
}

SAFE_MODIFIERS = ["technology", "digital", "abstract", "background", "concept", "innovation", "data", "circuit", "network", "cyber"]

def _extract_keywords(title, summary=""):
    import re
    text = f"{title} {summary}"
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                 "have", "has", "had", "do", "does", "did", "will", "would", "could",
                 "should", "may", "might", "shall", "can", "need", "dare", "ought",
                 "used", "with", "that", "this", "these", "those", "for", "and", "nor",
                 "but", "or", "yet", "so", "not", "to", "in", "on", "at", "by", "from",
                 "of", "off", "out", "up", "down", "into", "over", "under", "again",
                 "further", "then", "once", "here", "there", "when", "where", "why",
                 "how", "all", "each", "every", "both", "few", "more", "most", "other",
                 "some", "such", "after", "before", "between", "through", "during",
                 "their", "they", "them", "its", "it", "he", "she", "we", "you", "me",
                 "who", "whom", "which", "what", "than"}
    words = [w for w in text.split() if w.lower() not in stopwords and len(w) > 3 and w.lower() not in BLOCKED_KEYWORDS]
    seen = set()
    unique = []
    for w in words:
        lw = w.lower()
        if lw not in seen:
            seen.add(lw)
            unique.append(w)
    return unique[:3] if unique else ["AI", "technology"]


def _download_images(keywords, count=3):
    import random
    img_paths = []
    output_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
    os.makedirs(output_dir, exist_ok=True)

    pexels_key = os.getenv("PEXELS_API_KEY", "")
    if pexels_key:
        for kw in keywords[:2]:
            safe_kw = kw
            modifier = random.choice(SAFE_MODIFIERS)
            query = f"{safe_kw} {modifier}"
            try:
                resp = __import__("requests").get(
                    f"https://api.pexels.com/v1/search?query={query}&per_page=5&orientation=landscape&size=large",
                    headers={"Authorization": pexels_key},
                    timeout=10,
                )
                if resp.status_code == 200:
                    photos = resp.json().get("photos", [])
                    for photo in photos:
                        alt = (photo.get("alt", "") or "").lower()
                        if any(b in alt for b in BLOCKED_KEYWORDS):
                            continue
                        for size_key in ["original", "large2x", "large"]:
                            img_url = photo.get("src", {}).get(size_key, "")
                            if img_url:
                                break
                        if not img_url:
                            continue
                        img_resp = __import__("requests").get(img_url, timeout=20)
                        if img_resp.status_code == 200:
                            fname = f"{safe_kw}_{len(img_paths)}.jpg"
                            fpath = os.path.join(output_dir, fname)
                            with open(fpath, "wb") as f:
                                f.write(img_resp.content)
                            img_paths.append(fpath)
                            if len(img_paths) >= count:
                                return img_paths
            except Exception:
                continue

    stock_urls = [
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1280&h=720&fit=crop",
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1280&h=720&fit=crop",
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1280&h=720&fit=crop",
        "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=1280&h=720&fit=crop",
        "https://images.unsplash.com/photo-1531746790095-e5cb15765ec7?w=1280&h=720&fit=crop",
    ]
    for url in stock_urls:
        try:
            resp = __import__("requests").get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                fname = f"stock_{len(img_paths)}.jpg"
                fpath = os.path.join(output_dir, fname)
                with open(fpath, "wb") as f:
                    f.write(resp.content)
                img_paths.append(fpath)
                if len(img_paths) >= count:
                    return img_paths
        except Exception:
            continue

    return img_paths or _generate_fallback_images(count)


def _generate_fallback_images(count=3):
    W, H = 1280, 720
    output_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    from PIL import Image, ImageDraw
    for i in range(count):
        img = Image.new("RGB", (W, H), (random.randint(5, 30), random.randint(5, 30), random.randint(30, 60)))
        draw = ImageDraw.Draw(img)
        for _ in range(random.randint(5, 15)):
            x, y = random.randint(0, W), random.randint(0, H)
            r = random.randint(20, 100)
            draw.ellipse(
                [x - r, y - r, x + r, y + r],
                fill=(random.randint(30, 100), random.randint(30, 100), random.randint(80, 150)),
            )
        fpath = os.path.join(output_dir, f"fallback_{i}.jpg")
        img.save(fpath, quality=85)
        paths.append(fpath)
    return paths


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


def create_news_video(news_items, script, output_path="ai_news_video.mp4"):
    from moviepy import (
        VideoFileClip,
        ImageClip,
        AudioFileClip,
        TextClip,
        CompositeVideoClip,
        concatenate_videoclips,
        concatenate_audioclips,
    )

    os.makedirs(os.path.join(os.path.dirname(__file__), "assets"), exist_ok=True)

    print("[+] Generating voiceover...")
    tts = gTTS(text=script, lang="en", slow=False)
    audio_path = os.path.join(os.path.dirname(__file__), "assets", "narration.mp3")
    tts.save(audio_path)
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    print(f"[+] Audio duration: {audio_duration:.1f}s")
    print("[+] Creating video segments...")

    segments = []
    segment_duration = audio_duration / (len(news_items) + 1)

    intro_img = create_text_image("AI News Update\nTop Stories Today", bg_color=(10, 10, 35))
    intro_clip = ImageClip(intro_img, duration=segment_duration).with_fps(12)
    segments.append(intro_clip)

    for item in news_items:
        keywords = _extract_keywords(item["title"], item.get("summary", ""))
        img_paths = _download_images(keywords, count=2)
        W, H = 1280, 720
        if img_paths:
            clip = ImageClip(img_paths[0], duration=segment_duration).with_fps(12)
            clip = clip.resized(width=W)
            if clip.h < H:
                clip = clip.resized(height=H)
            clip = clip.cropped(x_center=clip.w / 2, y_center=clip.h / 2, width=W, height=H)
        else:
            clip = create_text_image(item["title"], bg_color=(20, 20, 50))
            clip = ImageClip(clip, duration=segment_duration).with_fps(24)

        txt_clip = TextClip(
            text=item["title"],
            font_size=28,
            color="white",
            stroke_color="black",
            stroke_width=2,
            font=_get_font_path(),
            method="caption",
            size=(1200, None),
        ).with_duration(segment_duration).with_position(("center", "bottom")).with_start(0)

        overlay = CompositeVideoClip([clip, txt_clip])
        segments.append(overlay)

    print("[+] Concatenating video...")
    final_video = concatenate_videoclips(segments, method="compose")

    final_video = final_video.with_duration(audio_duration)
    final_video = final_video.with_audio(audio)
    final_video = final_video.resized(height=720)

    print(f"[+] Writing video to {output_path}...")
    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=12,
        bitrate="1000k",
        preset="ultrafast",
        threads=4,
    )

    final_video.close()
    audio.close()

    return output_path


def create_shorts(news_items, script, output_path="ai_shorts.mp4"):
    from moviepy import (
        ImageClip,
        AudioFileClip,
        TextClip,
        CompositeVideoClip,
        concatenate_videoclips,
    )

    os.makedirs(os.path.join(os.path.dirname(__file__), "assets"), exist_ok=True)

    print("[+] Generating Shorts voiceover...")
    short_script = script[:800]
    tts = gTTS(text=short_script, lang="en", slow=False)
    audio_path = os.path.join(os.path.dirname(__file__), "assets", "shorts_narration.mp3")
    tts.save(audio_path)
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    W, H = 1080, 1920
    segments = []
    seg_dur = audio_duration / max(len(news_items) + 1, 1)

    intro = ImageClip(
        Image.new("RGB", (W, H), (10, 10, 35)), duration=seg_dur
    )
    txt_intro = TextClip(
        text="AI NEWS\nTODAY",
        font_size=80, color="white", font=_get_font_path(),
        stroke_color="black", stroke_width=3, method="caption",
        size=(W - 80, None),
    ).with_duration(seg_dur).with_position("center").with_start(0)
    segments.append(CompositeVideoClip([intro, txt_intro]))

    for item in news_items:
        keywords = _extract_keywords(item["title"], item.get("summary", ""))
        img_paths = _download_images(keywords, count=1)
        bg_clip = ImageClip(img_paths[0], duration=seg_dur).with_fps(12) if img_paths else ImageClip(
            Image.new("RGB", (W, H), (20, 20, 50)), duration=seg_dur
        )
        bg_clip = bg_clip.resized(width=W).cropped(x_center=bg_clip.w / 2, y_center=bg_clip.h / 2, width=W, height=H)

        txt = TextClip(
            text=item["title"],
            font_size=36, color="white", font=_get_font_path(),
            stroke_color="black", stroke_width=2, method="caption",
            size=(W - 60, None),
        ).with_duration(seg_dur).with_position(("center", H - 300)).with_start(0)

        segments.append(CompositeVideoClip([bg_clip, txt]))

    final = concatenate_videoclips(segments, method="compose")
    final = final.with_duration(audio_duration).with_audio(audio)

    print(f"[+] Writing Shorts to {output_path}...")
    final.write_videofile(
        output_path, codec="libx264", audio_codec="aac",
        fps=12, bitrate="2000k", preset="ultrafast", threads=4,
    )
    final.close()
    audio.close()
    return output_path
