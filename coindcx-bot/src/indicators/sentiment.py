import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from src.config import settings


class SentimentAnalyzer:
    def __init__(self):
        self._http: Optional[httpx.AsyncClient] = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=15)
        return self._http

    async def compute_all(self) -> Dict[str, Any]:
        results = {
            "fear_greed": await self._fear_greed_index(),
            "btc_dominance": await self._btc_dominance(),
            "altcoin_season": await self._altcoin_season_index(),
            "news_sentiment": await self._news_sentiment(),
            "social_sentiment": await self._social_sentiment(),
        }
        results["overall_sentiment"] = self._calculate_overall(results)
        return results

    async def _fear_greed_index(self) -> Dict:
        try:
            http = await self._get_http()
            resp = await http.get(
                "https://api.alternative.me/fng/?limit=7",
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()["data"]
                current = int(data[0]["value"])
                prev_values = [int(d["value"]) for d in data[1:]]
                trend = "increasing" if current > sum(prev_values) / len(prev_values) else "decreasing"
                return {
                    "value": current,
                    "classification": self._classify_fear_greed(current),
                    "trend": trend,
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            logger.warning(f"Failed to fetch fear & greed index: {e}")
        return {"value": 50, "classification": "neutral", "trend": "neutral"}

    def _classify_fear_greed(self, value: int) -> str:
        if value <= 25:
            return "extreme_fear"
        elif value <= 40:
            return "fear"
        elif value <= 60:
            return "neutral"
        elif value <= 75:
            return "greed"
        else:
            return "extreme_greed"

    async def _btc_dominance(self) -> Dict:
        try:
            http = await self._get_http()
            resp = await http.get(
                "https://api.coingecko.com/api/v3/global",
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()["data"]
                dom = data["market_cap_percentage"]["btc"]
                return {
                    "value": dom,
                    "classification": "high" if dom > 60 else "medium" if dom > 40 else "low",
                    "altcoin_season": dom < 40,
                }
        except Exception as e:
            logger.warning(f"Failed to fetch BTC dominance: {e}")
        return {"value": 50, "classification": "medium", "altcoin_season": False}

    async def _altcoin_season_index(self) -> Dict:
        try:
            http = await self._get_http()
            resp = await http.get(
                "https://api.alternative.me/altseason/?limit=1",
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()["data"]
                value = int(data[0]["altseason"])
                return {
                    "value": value,
                    "is_altseason": value >= 75,
                    "classification": "altseason" if value >= 75 else "bitcoin_season" if value <= 25 else "transition",
                }
        except Exception:
            pass

        btc_dom = await self._btc_dominance()
        is_altseason = btc_dom.get("value", 50) < 40
        return {
            "value": 75 if is_altseason else 25,
            "is_altseason": is_altseason,
            "classification": "altseason" if is_altseason else "bitcoin_season",
        }

    async def _news_sentiment(self) -> Dict:
        try:
            if not settings.newsapi_key:
                return {"score": 0, "classification": "neutral", "sources": 0}

            http = await self._get_http()
            resp = await http.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": "cryptocurrency OR bitcoin OR crypto trading",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 20,
                    "apiKey": settings.newsapi_key,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                articles = resp.json().get("articles", [])
                positive_keywords = ["bullish", "surge", "rally", "gain", "upgrade", "adoption", "institutional"]
                negative_keywords = ["bearish", "crash", "dump", "ban", "hack", "regulation", "crackdown"]

                pos_count = sum(
                    1 for a in articles
                    if any(kw in (a.get("title", "") + a.get("description", "")).lower() for kw in positive_keywords)
                )
                neg_count = sum(
                    1 for a in articles
                    if any(kw in (a.get("title", "") + a.get("description", "")).lower() for kw in negative_keywords)
                )
                total = pos_count + neg_count
                score = ((pos_count - neg_count) / total * 100) if total > 0 else 0

                return {
                    "score": score,
                    "classification": "positive" if score > 20 else "negative" if score < -20 else "neutral",
                    "sources": len(articles),
                }
        except Exception as e:
            logger.warning(f"Failed to fetch news sentiment: {e}")
        return {"score": 0, "classification": "neutral", "sources": 0}

    async def _social_sentiment(self) -> Dict:
        return {"score": 0, "classification": "neutral", "platforms": ["twitter", "reddit"]}

    def _calculate_overall(self, data: Dict) -> Dict:
        scores = []
        if "fear_greed" in data:
            fg = data["fear_greed"].get("value", 50)
            scores.append((fg - 50) / 50 * 100)

        if "btc_dominance" in data:
            dom = data["btc_dominance"].get("value", 50)
            scores.append((50 - dom) * 2)

        if "news_sentiment" in data:
            scores.append(data["news_sentiment"].get("score", 0))

        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "score": avg_score,
            "classification": "bullish" if avg_score > 20 else "bearish" if avg_score < -20 else "neutral",
            "strength": "strong" if abs(avg_score) > 40 else "moderate" if abs(avg_score) > 20 else "weak",
        }

    async def analyze_social_mentions(self, coin: str) -> Dict:
        return {
            "coin": coin,
            "positive_mentions": 0,
            "negative_mentions": 0,
            "total_mentions": 0,
            "sentiment_score": 0,
        }

    async def close(self):
        if self._http:
            await self._http.aclose()
