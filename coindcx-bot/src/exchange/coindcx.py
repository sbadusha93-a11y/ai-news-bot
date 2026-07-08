import asyncio
import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pandas as pd
from loguru import logger

from src.config import settings


class CoinDCXExchange:
    def __init__(self):
        self.api_key = settings.coin_dcx_api_key
        self.api_secret = settings.coin_dcx_api_secret
        self.base_url = "https://api.coindcx.com"
        self._http_client: Optional[httpx.AsyncClient] = None
        self._rate_limiter = asyncio.Semaphore(20)
        self._last_request_time = 0
        self._min_request_interval = 0.05
        self._rate_lock = asyncio.Lock()
        self._pair_cache: Dict[str, str] = {}
        self._pair_cache_loaded = False
        self._pair_cache_lock = asyncio.Lock()
        self._max_retries = 2
        self._active_futures: Dict[str, bool] = {}
        self._active_futures_loaded = False
        self._active_futures_lock = asyncio.Lock()

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=30,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return self._http_client

    async def _rate_limit(self):
        async with self._rate_lock:
            now = time.time()
            elapsed = now - self._last_request_time
            wait = max(0, self._min_request_interval - elapsed)
        if wait > 0:
            await asyncio.sleep(wait)
        async with self._rate_lock:
            self._last_request_time = time.time()

    def _sign_request(self, payload: Dict) -> Dict:
        json_payload = json.dumps(payload, separators=(",", ":"))
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            json_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": self.api_key,
            "X-AUTH-SIGNATURE": signature,
        }

    async def _ensure_pair_cache(self):
        if self._pair_cache_loaded:
            return
        async with self._pair_cache_lock:
            if self._pair_cache_loaded:
                return
            try:
                http = await self._get_http()
                resp = await asyncio.wait_for(
                    http.get(f"{self.base_url}/exchange/v1/markets_details"), timeout=10
                )
                if resp.status_code == 200:
                    for m in resp.json():
                        self._pair_cache[m["coindcx_name"]] = m["pair"]
                    self._pair_cache_loaded = True
                    logger.debug(f"Loaded {len(self._pair_cache)} pair mappings")
            except Exception as e:
                logger.warning(f"Failed to load pair cache: {e}")

    def _get_coin_dcx_pair(self, symbol: str) -> str:
        name = symbol.replace("_", "")
        cached = self._pair_cache.get(name)
        if cached:
            return cached
        parts = symbol.split("_")
        if len(parts) == 3:
            return f"{parts[0]}-{parts[1]}_{parts[2]}"
        if len(parts) == 2:
            return f"B-{parts[0]}_{parts[1]}"
        for q in ["USDT", "BTC", "INR", "ETH", "USDC", "BUSD", "DAI", "PAX"]:
            if name.endswith(q) and len(name) > len(q):
                return f"B-{name[:-len(q)]}_{q}"
        return symbol

    async def fetch_ohlcv(
        self, symbol: str, timeframe: str = "4h", limit: int = 200
    ) -> List[List[float]]:
        await self._ensure_pair_cache()
        last_error = None
        max_attempts = 1
        for attempt in range(max_attempts):
            async with self._rate_limiter:
                await self._rate_limit()
                try:
                    http = await self._get_http()
                    pair = self._get_coin_dcx_pair(symbol)

                    tf_map = {
                        "1m": "1m", "5m": "1m", "15m": "15m", "30m": "1m",
                        "1h": "1h", "2h": "1h", "4h": "1h", "6h": "1h",
                        "8h": "1h", "12h": "1h", "1d": "1d", "3d": "1d", "1w": "1d",
                    }
                    resolution = tf_map.get(timeframe, "1h")
                    aggregation_map = {
                        "1m": ("1m", 1), "5m": ("5m", 5), "15m": ("15m", 15), "30m": ("30m", 30),
                        "1h": ("1h", 60), "2h": ("2h", 120), "4h": ("4h", 240), "6h": ("6h", 360),
                        "8h": ("8h", 480), "12h": ("12h", 720), "1d": ("1d", 1440), "3d": ("3d", 4320), "1w": ("1w", 10080),
                    }
                    pd_label, agg = aggregation_map.get(timeframe, ("1h", 60))

                    base_limit = {"1m": 500, "15m": 500, "1h": 500, "1d": 500}.get(resolution, 500)
                    fetch_limit = min(int(limit * max(agg / 60, 1) * 1.5), base_limit)

                    resp = await http.get(
                        f"{self.base_url}/market_data/candles",
                        params={"pair": pair, "interval": resolution, "limit": fetch_limit},
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        df = pd.DataFrame(data)
                        if df.empty:
                            return []
                        df["time"] = pd.to_datetime(df["time"], unit="ms")
                        df.set_index("time", inplace=True)
                        for col in ["open", "high", "low", "close", "volume"]:
                            df[col] = df[col].astype(float)

                        if pd_label != resolution:
                            df = df.resample(pd_label).agg({
                                "open": "first",
                                "high": "max",
                                "low": "min",
                                "close": "last",
                                "volume": "sum",
                            }).dropna()

                        df = df.tail(limit)
                        ohlcv = []
                        for idx, row in df.iterrows():
                            ohlcv.append([
                                int(idx.timestamp() * 1000),
                                row["open"], row["high"], row["low"],
                                row["close"], row["volume"],
                            ])
                        return ohlcv
                    return []
                except httpx.ConnectError as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(1)
                    else:
                        logger.debug(f"Failed to fetch OHLCV for {symbol}: {e}")
                        return []
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(1)
                    else:
                        logger.debug(f"Failed to fetch OHLCV for {symbol}: {e}")
                        return []

    async def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        async with self._rate_limiter:
            await self._rate_limit()
            try:
                http = await self._get_http()
                pair = self._get_coin_dcx_pair(symbol)
                resp = await http.get(
                    f"{self.base_url}/exchange/v1/derivatives/futures/ticker",
                    params={"pair": pair},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "symbol": symbol,
                        "last": float(data.get("last_price", 0)),
                        "bid": float(data.get("bid", 0)),
                        "ask": float(data.get("ask", 0)),
                        "high": float(data.get("high", 0)),
                        "low": float(data.get("low", 0)),
                        "volume": float(data.get("volume", 0)),
                        "change": float(data.get("change", 0)),
                    }
                return None
            except Exception as e:
                logger.debug(f"Failed to fetch ticker for {symbol}: {e}")
                return None

    async def fetch_all_tickers(self, quote_currency: str = "USDT") -> Dict[str, Dict]:
        async with self._rate_limiter:
            await self._rate_limit()
            try:
                http = await self._get_http()
                resp = await http.get(f"{self.base_url}/exchange/ticker")
                if resp.status_code == 200:
                    data = resp.json()
                    tickers = {}
                    for item in data:
                        name = item.get("market", "")
                        if not name.endswith(quote_currency):
                            continue
                        symbol = name.replace("-", "_")
                        tickers[symbol] = {
                            "symbol": symbol,
                            "last": float(item.get("last_price", 0)),
                            "bid": float(item.get("bid", 0)),
                            "ask": float(item.get("ask", 0)),
                            "high": float(item.get("high", 0)),
                            "low": float(item.get("low", 0)),
                            "volume": float(item.get("volume", 0)),
                            "baseVolume": float(item.get("volume", 0)),
                            "quoteVolume": float(item.get("volume", 0)) * float(item.get("last_price", 0)),
                            "percentage": float(item.get("change_24_hour", 0)),
                        }
                    return tickers
                return {}
            except Exception as e:
                logger.error(f"Failed to fetch all tickers: {e}")
                return {}

    async def fetch_balance(self) -> Dict:
        if not self.api_key or not self.api_secret:
            return {"info": {"message": "API keys not configured"}}
        async with self._rate_limiter:
            await self._rate_limit()
            try:
                http = await self._get_http()
                payload = {"timestamp": int(time.time() * 1000)}
                headers = self._sign_request(payload)
                resp = await http.post(
                    f"{self.base_url}/exchange/v1/users/balances",
                    headers=headers, data=json.dumps(payload),
                )
                if resp.status_code == 200:
                    return resp.json()
                return {}
            except Exception as e:
                logger.error(f"Failed to fetch balance: {e}")
                return {}

    async def create_order(self, symbol: str, order_type: str, side: str,
                           amount: float, price: Optional[float] = None) -> Optional[Dict]:
        if not self.api_key or not self.api_secret:
            return {"message": "API keys not configured"}
        async with self._rate_limiter:
            await self._rate_limit()
            try:
                http = await self._get_http()
                payload = {
                    "side": side.upper(),
                    "order_type": order_type.upper(),
                    "market": symbol.replace("_", ""),
                    "price_per_unit": price or 0,
                    "total_quantity": amount,
                    "timestamp": int(time.time() * 1000),
                }
                headers = self._sign_request(payload)
                resp = await http.post(
                    f"{self.base_url}/exchange/v1/orders/create",
                    headers=headers, data=json.dumps(payload),
                )
                if resp.status_code == 200:
                    return resp.json()
                return None
            except Exception as e:
                logger.error(f"Failed to create order: {e}")
                return None

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        if not self.api_key or not self.api_secret:
            return False
        async with self._rate_limiter:
            await self._rate_limit()
            try:
                http = await self._get_http()
                payload = {"id": order_id, "timestamp": int(time.time() * 1000)}
                headers = self._sign_request(payload)
                resp = await http.post(
                    f"{self.base_url}/exchange/v1/orders/cancel",
                    headers=headers, data=json.dumps(payload),
                )
                return resp.status_code == 200
            except Exception as e:
                logger.error(f"Failed to cancel order: {e}")
                return False

    async def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        if not self.api_key or not self.api_secret:
            return []
        async with self._rate_limiter:
            await self._rate_limit()
            try:
                http = await self._get_http()
                payload = {"timestamp": int(time.time() * 1000)}
                if symbol:
                    payload["market"] = symbol.replace("_", "")
                headers = self._sign_request(payload)
                resp = await http.post(
                    f"{self.base_url}/exchange/v1/orders/active",
                    headers=headers, data=json.dumps(payload),
                )
                if resp.status_code == 200:
                    return resp.json()
                return []
            except Exception as e:
                logger.error(f"Failed to fetch open orders: {e}")
                return []

    async def get_instruments(self) -> List[Dict]:
        try:
            http = await self._get_http()
            resp = await http.get(f"{self.base_url}/exchange/v1/markets")
            if resp.status_code == 200:
                return resp.json()
            return []
        except Exception as e:
            logger.error(f"Failed to get instruments: {e}")
            return []

    async def get_markets_details(self) -> List[Dict]:
        try:
            http = await self._get_http()
            resp = await http.get(f"{self.base_url}/exchange/v1/markets_details")
            if resp.status_code == 200:
                return resp.json()
            return []
        except Exception as e:
            logger.error(f"Failed to get market details: {e}")
            return []

    async def _ensure_active_futures(self):
        if self._active_futures_loaded:
            return
        async with self._active_futures_lock:
            if self._active_futures_loaded:
                return
            try:
                http = await self._get_http()
                resp = await asyncio.wait_for(
                    http.get(f"{self.base_url}/exchange/v1/derivatives/futures/markets"),
                    timeout=10,
                )
                if resp.status_code == 200:
                    for m in resp.json():
                        pair = m.get("pair", "")
                        status = m.get("status", "inactive")
                        self._active_futures[pair] = status == "active"
                    self._active_futures_loaded = True
                    logger.debug(f"Loaded {len(self._active_futures)} futures markets")
            except Exception as e:
                logger.warning(f"Failed to load active futures: {e}")

    async def is_futures_active(self, symbol: str) -> bool:
        await self._ensure_active_futures()
        if not self._active_futures_loaded:
            return True
        pair = self._get_coin_dcx_pair(symbol)
        return self._active_futures.get(pair, True)

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
