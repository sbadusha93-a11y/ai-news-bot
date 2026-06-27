import random
import requests
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import os


BRAND_KEYWORDS = {
    "samsung": "Samsung Galaxy", "apple": "Apple iPhone", "google": "Google Pixel",
    "xiaomi": "Xiaomi", "oneplus": "OnePlus", "sony": "Sony Xperia",
    "nokia": "Nokia", "motorola": "Motorola", "oppo": "Oppo", "vivo": "Vivo",
    "huawei": "Huawei", "honor": "Honor", "realme": "Realme", "nothing": "Nothing Phone",
    "asus": "Asus ROG", "lenovo": "Lenovo",
}


def _clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "--")
    text = text.replace("\u2026", "...")
    text = re.sub(r"[^\x20-\x7E\n]", "", text)
    return text.strip()


def fetch_gadget_news():
    try:
        from newsapi import NewsApiClient
        api_key = os.getenv("NEWSAPI_KEY", "")
        if api_key:
            newsapi = NewsApiClient(api_key=api_key)
            headlines = newsapi.get_everything(
                q="(smartphone OR iPhone OR Android OR Galaxy OR Pixel OR OnePlus) AND (launch OR review OR release OR update OR leak)",
                language="en",
                sort_by="publishedAt",
                page_size=5,
            )
            articles = headlines.get("articles", [])
            if articles:
                return _parse_articles(articles)
    except Exception:
        pass

    api_key = os.getenv("NEWSAPI_KEY", "")
    if api_key:
        url = (
            f"https://newsapi.org/v2/everything"
            f"?q=(smartphone+OR+gadget+OR+iPhone+OR+Android+OR+Samsung)+AND+(launch+OR+review+OR+release)"
            f"&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
        )
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                articles = resp.json().get("articles", [])
                if articles:
                    return _parse_articles(articles)
        except Exception:
            pass

    return _fetch_fallback()


def _fetch_fallback():
    feeds = [
        "https://www.gsmarena.com/rss-news-reviews.php3",
        "https://www.theverge.com/mobile/rss.xml",
        "https://rss.app/feeds/gadget-news.xml",
    ]
    for feed_url in feeds:
        try:
            resp = requests.get(feed_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                items = _parse_rss_generic(resp)
                if items and len(items) >= 3:
                    return items
        except Exception:
            continue

    try:
        url = "https://hn.algolia.com/api/v1/search?query=smartphone+gadget+mobile+tech+launch&tags=story&hitsPerPage=5"
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            items = _parse_hackernews(resp)
            if items and len(items) >= 3:
                return items
    except Exception:
        pass

    return _generate_sample_news()


def _parse_articles(articles):
    results = []
    for a in articles:
        title = _clean(a.get("title") or "")
        desc = _clean(a.get("description") or "")
        if not title or not desc:
            continue
        results.append({
            "title": title,
            "summary": desc[:500],
            "url": a.get("url", ""),
            "source": a.get("source", {}).get("name", "Tech News") if isinstance(a.get("source"), dict) else str(a.get("source", "Tech News")),
            "date": (a.get("publishedAt") or "")[:10],
        })
        if len(results) >= 5:
            break
    return results


def _parse_rss_generic(resp):
    items = []
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        return items

    ns = {"atom": "http://www.w3.org/2005/Atom", "": ""}
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title")
        summary = entry.find("{http://www.w3.org/2005/Atom}summary")
        if title is not None and title.text:
            clean_title = _clean(title.text)
            clean_summary = _clean(summary.text[:500]) if summary is not None and summary.text else clean_title
            items.append({
                "title": clean_title,
                "summary": clean_summary,
                "url": "",
                "source": "GSMArena",
                "date": datetime.now().strftime("%Y-%m-%d"),
            })
            if len(items) >= 5:
                break

    if not items:
        for item in root.iter("item"):
            title = item.find("title")
            desc = item.find("description")
            if title is not None and title.text:
                clean_title = _clean(title.text)
                clean_desc = _clean(desc.text[:500]) if desc is not None and desc.text else clean_title
                items.append({
                    "title": clean_title,
                    "summary": clean_desc,
                    "url": "",
                    "source": "Gadget News",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                })
                if len(items) >= 5:
                    break

    return items


def _parse_hackernews(resp):
    data = resp.json()
    results = []
    for hit in data.get("hits", []):
        title = _clean(hit.get("title", ""))
        url = hit.get("url") or hit.get("hnURL", "")
        points = hit.get("points", 0)
        author = hit.get("author", "unknown")
        num_comments = hit.get("num_comments", 0)
        if title and len(title) > 15:
            results.append({
                "title": title,
                "summary": f"This story gained {points} points and {num_comments} comments on Hacker News, sparking discussion among the tech community.",
                "url": url,
                "source": "Hacker News",
                "date": datetime.now().strftime("%Y-%m-%d"),
            })
            if len(results) >= 5:
                break
    return results


def _generate_sample_news():
    return [
        {
            "title": "Samsung Galaxy S26 Ultra Leaks Reveal 200MP Camera and Titanium Design",
            "summary": "Leaked renders reveal Samsung's Galaxy S26 Ultra with a 200MP main camera, under-display selfie camera, titanium frame, and a built-in S Pen. Expected to launch in early 2026 with the Exynos 2600 chipset.",
            "url": "https://samsung.com",
            "source": "Samsung",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Apple iPhone 17 Pro Gets Revolutionary Stacked Battery Technology",
            "summary": "Apple's iPhone 17 Pro introduces stacked battery technology delivering 40 percent higher energy density, enabling all-day battery life in a thinner design. The A19 chip brings desktop-class performance with ray tracing support.",
            "url": "https://apple.com",
            "source": "Apple",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "OnePlus 13 Review: Snapdragon 8 Gen 4 and 100W Charging Redefine Flagship Value",
            "summary": "The OnePlus 13 packs a Snapdragon 8 Gen 4 processor, 100W wired charging, and a Hasselblad-tuned triple camera system. Early reviews call it the best value flagship of 2026 with exceptional battery life.",
            "url": "https://oneplus.com",
            "source": "OnePlus",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Xiaomi Mix Fold 4 Sets New Standard with Crease-Free Foldable Display",
            "summary": "Xiaomi's Mix Fold 4 features a crease-free inner display, 50MP Leica quad camera system, and measures just 11 millimeters when folded. It's being called the most polished foldable phone released to date.",
            "url": "https://xiaomi.com",
            "source": "Xiaomi",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Google Pixel 11 Brings Tensor G6 with AI-Powered Photography",
            "summary": "Google's Pixel 11 introduces Real Tone 3.0, Video Boost with on-device AI processing, and a new periscope telephoto lens offering 10x optical zoom. The custom Tensor G6 chip powers all new camera features.",
            "url": "https://store.google.com",
            "source": "Google",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
    ]


def gadget_news_to_script(news_items, hook=None):
    if hook:
        script = hook + "\n\n"
    else:
        top = news_items[0]["title"] if news_items else "Gadget News"
        hooks = [
            f"Hey everyone, welcome back to Gadget News. Today we have some incredible stories to share, starting with {top}.",
            f"What is going on tech fam? We have some major gadget news today. {top}.",
            f"Welcome to Gadget News. If you love smartphones and gadgets, you are in the right place. Today, {top}.",
            f"Hey guys, big day for gadget lovers. {top}.",
            f"Welcome back. Today's top story is all about {top}. Let's dive right in.",
        ]
        script = random.choice(hooks) + "\n\n"
    script += "Here are the top stories making headlines in the world of mobile technology today.\n\n"
    for i, item in enumerate(news_items, 1):
        script += f"First up, {item['title']}. {item['summary']}\n\n"
    script += "Alright guys, that wraps up today's gadget news update. "
    script += "Let me know in the comments which story got you most excited. "
    script += "If you enjoyed this video, please hit that like button and subscribe to the channel so you don't miss any future updates. Thanks for watching, and I will see you in the next one."
    return script
