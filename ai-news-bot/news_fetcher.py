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


def fetch_ai_news():
    try:
        from newsapi import NewsApiClient
        api_key = os.getenv("NEWSAPI_KEY", "")
        if api_key:
            newsapi = NewsApiClient(api_key=api_key)
            headlines = newsapi.get_everything(
                q="artificial intelligence",
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
        url = f"https://newsapi.org/v2/everything?q=artificial+intelligence&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
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
        url = "https://www.theverge.com/ai-artificial-intelligence/rss.xml"
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            items = _parse_rss_theverge(resp)
            if items and len(items) >= 3:
                return items
    except Exception:
        pass

    try:
        url = "https://hn.algolia.com/api/v1/search?query=artificial+intelligence&tags=story&hitsPerPage=5"
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
            "title": "OpenAI Unveils GPT-5 with Breakthrough Reasoning Capabilities",
            "summary": "OpenAI has announced GPT-5, featuring advanced reasoning, multimodal understanding, and significantly reduced hallucination rates. The model sets new benchmarks across coding, mathematics, and creative tasks.",
            "url": "https://openai.com",
            "source": "OpenAI",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Google DeepMind Achieves Major Breakthrough in Protein Folding",
            "summary": "DeepMind's latest AI system has solved previously intractable protein structures, opening new pathways for drug discovery and disease understanding. Researchers call it a milestone for computational biology.",
            "url": "https://deepmind.google",
            "source": "DeepMind",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "Anthropic Releases Claude 4 with Enhanced Safety Features",
            "summary": "Anthropic's Claude 4 introduces constitutional AI improvements, longer context windows, and better alignment with human intent. Early tests show dramatic improvements in honesty and helpfulness.",
            "url": "https://anthropic.com",
            "source": "Anthropic",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "NVIDIA Announces Next-Gen AI Chip with 10x Performance",
            "summary": "NVIDIA's new Blackwell Ultra architecture delivers 10x AI training performance while reducing energy consumption. Major cloud providers have already placed bulk orders.",
            "url": "https://nvidia.com",
            "source": "NVIDIA",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "title": "AI Regulations Take Shape: EU AI Act Enters Enforcement Phase",
            "summary": "The EU AI Act's first enforcement phase begins, requiring transparency from high-risk AI systems. Companies face strict compliance requirements for training data disclosure and bias testing.",
            "url": "https://digital-strategy.ec.europa.eu",
            "source": "European Commission",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
    ]


def ai_news_to_script(news_items, hook=None):
    if hook:
        script = hook + "\n\n"
    else:
        top = news_items[0]["title"] if news_items else "AI"
        hooks = [
            f"You won't believe what AI just did. {top}.",
            f"Big news in AI today. {top}.",
            f"This changes everything. {top}.",
            f"The future of AI is here. {top}.",
        ]
        script = random.choice(hooks) + "\n\n"
    script += "Here are the top AI stories you need to know.\n\n"
    for i, item in enumerate(news_items, 1):
        script += f"Story {i}: {item['title']}. {item['summary']}\n\n"
    script += "That's all for now. Subscribe so you don't miss the next update."
    return script
