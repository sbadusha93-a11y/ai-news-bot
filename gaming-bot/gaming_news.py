import random
import requests
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import os

ADULT_KEYWORDS = {
    "sex", "sexy", "sexual", "porn", "porno", "pornography", "nude", "naked",
    "erotic", "adult", "xxx", "18+", "nsfw", "lingerie", "bikini", "swimsuit",
    "model", "models", "onlyfans", "camgirl", "escort", "dating", "hookup",
    "milf", "boobs", "ass", "butt", "thong", "stripper", "stripclub",
    "hentai", "rule34", "lewd", "nsfw", "horny", "slut", "whore",
    "bdsm", "kink", "fetish", "masturbat", "orgasm", "penis", "vagina",
    "breast", "nipple", "panties", "underwear", "nudity", "explicit",
    "mature", "sensual", "seductive", "provocative",
}

MEGA_ADULT_BLOCK = {
    "sex", "porn", "nude", "naked", "erotic", "xxx", "nsfw", "hentai",
    "onlyfans", "escort", "milf", "boobs", "lewd", "horny", "slut",
    "bdsm", "fetish", "masturbat", "penis", "vagina", "nipple",
}


def _clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "--")
    text = text.replace("\u2026", "...")
    text = re.sub(r"[^\x20-\x7E\n]", "", text)
    return text.strip()


def _is_safe(text):
    lowered = text.lower()
    for word in MEGA_ADULT_BLOCK:
        if word in lowered:
            return False
    return True


def fetch_gaming_news():
    try:
        from newsapi import NewsApiClient
        api_key = os.getenv("NEWSAPI_KEY", "")
        if api_key:
            newsapi = NewsApiClient(api_key=api_key)
            headlines = newsapi.get_everything(
                q="(gaming OR video game OR PlayStation OR Xbox OR Nintendo OR PC gaming) -porn -adult -nsfw -sex",
                language="en",
                sort_by="publishedAt",
                page_size=10,
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
            f"?q=(gaming+OR+video+game+OR+PlayStation+OR+Xbox+OR+Nintendo+OR+PC+gaming)"
            f"+NOT+porn+NOT+adult+NOT+nsfw+NOT+sex"
            f"&language=en&sortBy=publishedAt&pageSize=10&apiKey={api_key}"
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
        "https://www.ign.com/rss/articles",
        "https://www.pcgamer.com/rss/",
        "https://www.gamespot.com/feeds/news/",
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

    return _generate_sample_news()


def _parse_articles(articles):
    results = []
    for a in articles:
        title = _clean(a.get("title") or "")
        desc = _clean(a.get("description") or "")
        if not title or not desc:
            continue
        if not _is_safe(title) or not _is_safe(desc):
            continue
        results.append({
            "title": title,
            "summary": desc[:500],
            "url": a.get("url", ""),
            "source": a.get("source", {}).get("name", "Gaming News") if isinstance(a.get("source"), dict) else str(a.get("source", "Gaming News")),
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

    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title")
        summary = entry.find("{http://www.w3.org/2005/Atom}summary")
        if title is not None and title.text:
            clean_title = _clean(title.text)
            clean_summary = _clean(summary.text[:500]) if summary is not None and summary.text else clean_title
            if not _is_safe(clean_title) or not _is_safe(clean_summary):
                continue
            items.append({
                "title": clean_title,
                "summary": clean_summary,
                "url": "",
                "source": "IGN",
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
                if not _is_safe(clean_title) or not _is_safe(clean_desc):
                    continue
                items.append({
                    "title": clean_title,
                    "summary": clean_desc,
                    "url": "",
                    "source": "Gaming News",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                })
                if len(items) >= 5:
                    break

    return items


def _generate_sample_news():
    return [
        {
            "title": "GTA 6 Release Date Finally Confirmed by Rockstar Games",
            "summary": "Rockstar Games has officially announced the release date for Grand Theft Auto VI. Set to launch in fall 2026, the game takes players back to Vice City with a brand new storyline, improved graphics, and massive open-world improvements. Pre-orders are expected to break records.",
            "url": "https://rockstargames.com",
            "source": "Rockstar Games",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "PlayStation 6 Revealed: Sony's Next-Gen Console Details Leak",
            "summary": "Details about Sony's upcoming PlayStation 6 have surfaced online, revealing a custom AMD processor with ray tracing 3.0, 4TB SSD, and full backward compatibility with PS5 and PS4 titles. The reveal event is expected later this year with a holiday 2027 launch window.",
            "url": "https://playstation.com",
            "source": "PlayStation",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Nintendo Switch 2 Breaks Sales Records in First Month",
            "summary": "Nintendo's latest console, the Switch 2, has sold over 10 million units in its first month, making it the fastest-selling console in history. The new Mario and Zelda titles have received critical acclaim, driving unprecedented demand worldwide.",
            "url": "https://nintendo.com",
            "source": "Nintendo",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Xbox Game Pass Hits 50 Million Subscribers Milestone",
            "summary": "Microsoft has announced that Xbox Game Pass has officially crossed 50 million subscribers. The service continues to grow with the addition of day-one releases, cloud gaming improvements, and new partnerships with major third-party developers.",
            "url": "https://xbox.com",
            "source": "Xbox",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Elden Ring 2 Officially Announced at Summer Game Fest",
            "summary": "FromSoftware has announced Elden Ring 2, the highly anticipated sequel to the award-winning action RPG. The trailer showcased a new setting inspired by Norse mythology, new gameplay mechanics, and a 2027 release window. Fans are calling it the most anticipated game of the decade.",
            "url": "https://fromsoftware.jp",
            "source": "FromSoftware",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
    ]


def gaming_news_to_script(news_items, hook=None):
    if hook:
        script = hook + "\n\n"
    else:
        top = news_items[0]["title"] if news_items else "Gaming News"
        hooks = [
            f"What is up gamers? Welcome back to Gaming News. Today we have some huge stories including {top}.",
            f"Hey everyone, welcome to the channel. If you love gaming, you are in the right place. Today, {top}.",
            f"Welcome back gamers. We have some massive news today starting with {top}.",
            f"Hey guys, big day for gaming. {top}. Let's get right into it.",
            f"Gaming fans, listen up. Today's top story is {top}. Here is everything you need to know.",
        ]
        script = random.choice(hooks) + "\n\n"
    script += "Here are the top gaming stories making headlines right now.\n\n"
    for i, item in enumerate(news_items, 1):
        script += f"First up, {item['title']}. {item['summary']}\n\n"
    script += "Alright guys, that wraps up today's gaming news update. "
    script += "Let me know in the comments which story got you most hyped. "
    script += "If you enjoyed this video, hit that like button and subscribe so you never miss an update. Thanks for watching and I will see you in the next one. Peace."
    return script
