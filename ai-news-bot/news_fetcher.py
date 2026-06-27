import random
import requests
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import os


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
                q="smartphone OR mobile OR gadget OR iPhone OR Android",
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
        url = f"https://newsapi.org/v2/everything?q=smartphone+gadget+mobile+tech&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
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
    try:
        url = "https://www.theverge.com/mobile/rss.xml"
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            items = _parse_rss_theverge(resp)
            if items and len(items) >= 3:
                return items
    except Exception:
        pass

    try:
        url = "https://hn.algolia.com/api/v1/search?query=smartphone+gadget+mobile+tech&tags=story&hitsPerPage=5"
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
            "source": a.get("source", {}).get("name", "News") if isinstance(a.get("source"), dict) else str(a.get("source", "News")),
            "date": (a.get("publishedAt") or "")[:10],
        })
        if len(results) >= 5:
            break
    return results


def _parse_rss_theverge(resp):
    root = ET.fromstring(resp.content)
    items = []
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
                "source": "The Verge",
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
        if title and ("AI" in title or "intelligence" in title.lower() or "machine learning" in title.lower()):
            if points > 100:
                impact = "major discussion"
            elif points > 50:
                impact = "popular discussion"
            else:
                impact = "notable discussion"
            results.append({
                "title": title,
                "summary": f"This story sparked widespread discussion on Hacker News, gathering {points} points and {num_comments} comments from the developer community.",
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
            "title": "Samsung Galaxy S26 Ultra Leaks Reveal 200MP Camera and New Design",
            "summary": "Leaked renders of the Samsung Galaxy S26 Ultra show a radical new design with a 200MP main camera, under-display selfie camera, and a titanium frame. Expected launch in early 2026.",
            "url": "https://samsung.com",
            "source": "Samsung",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Apple iPhone 17 Pro Gets Revolutionary Battery Technology",
            "summary": "Apple's iPhone 17 Pro introduces stacked battery technology with 40% higher density, enabling all-day battery life in a thinner form factor. The new A19 chip delivers desktop-class performance.",
            "url": "https://apple.com",
            "source": "Apple",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "OnePlus 13 Review: The Flagship Killer Returns",
            "summary": "OnePlus 13 brings Snapdragon 8 Gen 4, 100W charging, and a Hasselblad-tuned camera system at a competitive price. Early reviews praise its display and battery life.",
            "url": "https://oneplus.com",
            "source": "OnePlus",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Xiaomi Mix Fold 4 Sets New Standard for Foldable Phones",
            "summary": "Xiaomi's Mix Fold 4 features a crease-free inner display, 50MP Leica quad camera, and an ultra-thin 11mm folded design. It is being called the best foldable of 2026.",
            "url": "https://xiaomi.com",
            "source": "Xiaomi",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Google Pixel 11 Brings AI-Powered Camera Features",
            "summary": "Google's Pixel 11 introduces Real Tone 3.0, Video Boost using on-device AI, and a new telephoto lens with 10x optical zoom. The Tensor G6 chip powers all new camera features.",
            "url": "https://store.google.com",
            "source": "Google",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
    ]


def gadget_news_to_script(news_items, hook=None):
    if hook:
        script = hook + "\n\n"
    else:
        top = news_items[0]["title"] if news_items else "Gadget"
        hooks = [
            f"You won't believe what just launched. {top}.",
            f"Big news in the gadget world today. {top}.",
            f"This changes everything for mobile users. {top}.",
            f"The future of smartphones is here. {top}.",
        ]
        script = random.choice(hooks) + "\n\n"
    script += "Here are the top mobile and gadget stories you need to know.\n\n"
    for i, item in enumerate(news_items, 1):
        script += f"Story {i}: {item['title']}. {item['summary']}\n\n"
    script += "That's all for now. Subscribe so you don't miss the next gadget update."
    return script
