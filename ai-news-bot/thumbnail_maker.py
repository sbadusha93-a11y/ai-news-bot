import os
import random
from PIL import Image, ImageDraw, ImageFont


def _get_font_path(size=60):
    candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", size),
        ("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", size),
        (r"C:\Windows\Fonts\impact.ttf", size),
        (r"C:\Windows\Fonts\arialbd.ttf", size),
        (r"C:\Windows\Fonts\arial.ttf", size),
        (r"C:\Windows\Fonts\segoeui.ttf", size),
    ]
    for path, sz in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, sz)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
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


def generate_thumbnail(title, output_path=None, bg_image_path=None):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (10, 10, 35))
    draw = ImageDraw.Draw(img)

    accent = (0, 120, 255)
    accent2 = (255, 50, 50)

    for i in range(H):
        r = int(10 + (30 - 10) * (i / H))
        g = int(10 + (20 - 10) * (i / H))
        b = int(35 + (60 - 35) * (i / H))
        draw.line([(0, i), (W, i)], fill=(r, g, b))

    bar_height = 8
    draw.rectangle([(0, H - bar_height - 60), (W, H - bar_height - 60 + bar_height)], fill=accent)

    brand_font = _get_font_path(32)
    draw.text((30, H - 50), "GADGET NEWS", font=brand_font, fill=(200, 200, 255))

    headline = title[:80]
    headline_font = _get_font_path(56)
    lines = _wrap_text(headline, headline_font, W - 80, draw)
    max_lines = 4
    lines = lines[:max_lines]

    y_start = 80
    line_h = 70
    for i, line in enumerate(lines):
        y = y_start + i * line_h
        draw.text((37, y + 3), line, font=headline_font, fill=(0, 0, 0))
        draw.text((40, y), line, font=headline_font, fill=(255, 255, 255))
        draw.text((37, y - 3), line, font=headline_font, fill=(0, 0, 0))

    decor_y = y_start + len(lines) * line_h + 10
    draw.rectangle([(40, decor_y), (200, decor_y + 4)], fill=accent2)

    output_path = output_path or os.path.join(os.path.dirname(__file__), "assets", "thumbnail.jpg")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)
    return output_path
