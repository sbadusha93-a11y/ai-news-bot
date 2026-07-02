import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from loguru import logger

from src.config import bot_config
from src.exchange.coindcx import CoinDCXExchange


class DataFetcher:
    def __init__(self, exchange: CoinDCXExchange):
        self.exchange = exchange
        self.timeframe_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "2h": "2h",
            "4h": "4h",
            "6h": "6h",
            "8h": "8h",
            "12h": "12h",
            "1d": "1d",
            "3d": "3d",
            "1w": "1w",
        }
        self.timeframe_minutes = {
            "1m": 1, "5m": 5, "15m": 15, "30m": 30,
            "1h": 60, "2h": 120, "4h": 240, "6h": 360,
            "8h": 480, "12h": 720, "1d": 1440, "3d": 4320, "1w": 10080,
        }

    async def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str = "4h",
        limit: int = 500,
    ) -> pd.DataFrame:
        ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit)
        if not ohlcv:
            return pd.DataFrame()

        df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df.sort_index(inplace=True)
        return df

    async def fetch_multi_timeframe_data(
        self, symbol: str, timeframes: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        if timeframes is None:
            timeframes = [bot_config["timeframes"]["primary"]] + bot_config["timeframes"]["confirmation"]

        results = {}
        tasks = {}
        for tf in timeframes:
            limit = 300 if tf in ("15m", "1h") else 200
            tasks[tf] = self.fetch_historical_data(symbol, tf, limit=limit)

        tf_list = list(tasks.keys())
        data_list = await asyncio.gather(*[tasks[tf] for tf in tf_list])
        for tf, data in zip(tf_list, data_list):
            if not data.empty:
                results[tf] = data

        return results

    async def scan_all_markets(self) -> pd.DataFrame:
        tickers = await self.exchange.fetch_all_tickers()
        if not tickers:
            return pd.DataFrame()

        rows = []
        for symbol, ticker in tickers.items():
            pair = symbol.replace("/", "_")
            rows.append({
                "symbol": pair,
                "price": ticker.get("last", 0),
                "volume": ticker.get("quoteVolume", 0) or ticker.get("baseVolume", 0) * ticker.get("last", 0),
                "change": ticker.get("percentage", 0),
                "high": ticker.get("high", 0),
                "low": ticker.get("low", 0),
                "bid": ticker.get("bid", 0),
                "ask": ticker.get("ask", 0),
            })

        df = pd.DataFrame(rows)
        min_vol = bot_config["coin_selection"]["min_volume_usdt"]
        df = df[df["volume"] >= min_vol]
        df.sort_values("volume", ascending=False, inplace=True)
        top_n = bot_config["coin_selection"]["max_coins_to_scan"]
        return df.head(top_n)

    async def fetch_sentiment_data(self) -> Dict:
        return {
            "fear_greed": await self._fetch_fear_greed(),
            "btc_dominance": await self._fetch_btc_dominance(),
            "funding_rates": {},
            "open_interest": {},
        }

    async def _fetch_fear_greed(self) -> Optional[int]:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.alternative.me/fng/?limit=1",
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return int(data["data"][0]["value"])
        except Exception:
            pass
        return None

    async def _fetch_btc_dominance(self) -> Optional[float]:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.coingecko.com/api/v3/global",
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["data"]["market_cap_percentage"].get("btc")
        except Exception:
            pass
        return None

    async def close(self):
        await self.exchange.close()
