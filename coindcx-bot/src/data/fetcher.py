import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
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
        from_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        if from_date is None or limit <= 1000:
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

        all_dfs = []
        page_size = 1000
        tf_minutes = self.timeframe_minutes.get(timeframe, 60)
        end_ts = int(datetime.now().timestamp() * 1000)
        start_ts = int(from_date.timestamp() * 1000)

        while end_ts > start_ts and len(all_dfs) * page_size < limit:
            ohlcv = await self.exchange.fetch_ohlcv(
                symbol, timeframe, page_size, end_time=end_ts,
            )
            if not ohlcv:
                break
            df = pd.DataFrame(
                ohlcv,
                columns=["timestamp", "open", "high", "low", "close", "volume"],
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            df.sort_index(inplace=True)
            all_dfs.append(df)
            earliest = df.index[0]
            end_ts = int(earliest.timestamp() * 1000) - (tf_minutes * 60 * 1000)
            if len(all_dfs) > 50:
                break
            await asyncio.sleep(0.1)

        if not all_dfs:
            return pd.DataFrame()
        combined = pd.concat(all_dfs)
        combined = combined[~combined.index.duplicated(keep="first")]
        combined.sort_index(inplace=True)
        return combined.tail(limit)

    async def fetch_multi_timeframe_data(
        self, symbol: str, timeframes: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        if timeframes is None:
            timeframes = [bot_config["timeframes"]["primary"]] + bot_config["timeframes"]["confirmation"]

        results = {}
        async def _fetch_one(tf):
            try:
                return await asyncio.wait_for(
                    self.fetch_historical_data(symbol, tf, limit=300 if tf in ("15m", "1h") else 200),
                    timeout=45,
                )
            except asyncio.TimeoutError:
                return pd.DataFrame()
            except Exception:
                return pd.DataFrame()
        data_list = await asyncio.gather(*[_fetch_one(tf) for tf in timeframes])
        for tf, data in zip(timeframes, data_list):
            if not data.empty:
                results[tf] = data
        return results

    async def scan_all_markets(self, quote_currency: str = "USDT") -> pd.DataFrame:
        tickers = await self.exchange.fetch_all_tickers(quote_currency)
        if not tickers:
            return pd.DataFrame()

        rows = []
        for symbol, ticker in tickers.items():
            if not symbol.endswith(quote_currency):
                continue
            rows.append({
                "symbol": symbol,
                "price": ticker.get("last", 0),
                "volume": ticker.get("quoteVolume") or (ticker.get("baseVolume", 0) * ticker.get("last", 0)),
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
        return {"fear_greed": None, "btc_dominance": None, "funding_rates": {}, "open_interest": {}}

    async def _get_http(self) -> httpx.AsyncClient:
        if not hasattr(self, '_http_client') or self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=10)
        return self._http_client

    async def _fetch_fear_greed(self) -> Optional[int]:
        try:
            client = await self._get_http()
            resp = await asyncio.wait_for(
                client.get("https://api.alternative.me/fng/?limit=1"), timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return int(data["data"][0]["value"])
        except Exception:
            pass
        return None

    async def _fetch_btc_dominance(self) -> Optional[float]:
        try:
            client = await self._get_http()
            resp = await asyncio.wait_for(
                client.get("https://api.coingecko.com/api/v3/global"), timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["data"]["market_cap_percentage"].get("btc")
        except Exception:
            pass
        return None

    async def close(self):
        if hasattr(self, '_http_client') and self._http_client is not None:
            await self._http_client.aclose()
        await self.exchange.close()
