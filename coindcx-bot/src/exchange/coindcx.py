import asyncio
import hashlib
import hmac
import json
import time
import traceback
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pandas as pd
from loguru import logger

from src.config import settings


FALLBACK_SYMBOLS = [
    "BTC_USDT", "ETH_USDT", "BNB_USDT", "SOL_USDT", "XRP_USDT",
    "ADA_USDT", "DOGE_USDT", "DOT_USDT", "LINK_USDT", "AVAX_USDT",
    "MATIC_USDT", "ATOM_USDT", "UNI_USDT", "LTC_USDT", "BCH_USDT",
    "XLM_USDT", "TRX_USDT", "FIL_USDT", "APT_USDT", "ARB_USDT",
]


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
        self._pair_cache_ttl = 3600
        self._pair_cache_loaded_at = 0
        self._max_retries = 2
        self._active_futures: Dict[str, bool] = {}
        self._active_futures_loaded = False
        self._active_futures_lock = asyncio.Lock()
        self._ohlcv_cache: Dict[str, tuple] = {}
        self._ohlcv_cache_ttl = 120

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
        now = time.time()
        if self._pair_cache_loaded and (now - self._pair_cache_loaded_at) < self._pair_cache_ttl:
            return
        async with self._pair_cache_lock:
            if self._pair_cache_loaded and (now - self._pair_cache_loaded_at) < self._pair_cache_ttl:
                return
            try:
                http = await self._get_http()
                resp = await asyncio.wait_for(
                    http.get(f"{self.base_url}/exchange/v1/markets_details"), timeout=15
                )
                if resp.status_code == 200:
                    for m in resp.json():
                        self._pair_cache[m["coindcx_name"]] = m["pair"]
                    self._pair_cache_loaded = True
                    self._pair_cache_loaded_at = time.time()
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
            result = f"{parts[0]}-{parts[1]}_{parts[2]}"
        elif len(parts) == 2:
            result = f"B-{parts[0]}_{parts[1]}"
        else:
            found = False
            result = symbol
            for q in ["USDT", "BTC", "INR", "ETH", "USDC", "BUSD", "DAI", "PAX"]:
                if name.endswith(q) and len(name) > len(q):
                    result = f"B-{name[:-len(q)]}_{q}"
                    found = True
                    break
            if not found:
                logger.warning(f"No pair mapping found for {symbol}, using raw")
        return result

    def _ohlcv_cache_key(self, symbol: str, timeframe: str, limit: int) -> str:
        return f"{symbol}:{timeframe}:{limit}"

    async def fetch_ohlcv(
        self, symbol: str, timeframe: str = "4h", limit: int = 200,
        start_time: Optional[int] = None, end_time: Optional[int] = None,
    ) -> List[List[float]]:
        if start_time is None and end_time is None:
            cache_key = self._ohlcv_cache_key(symbol, timeframe, limit)
            cached = self._ohlcv_cache.get(cache_key)
            if cached:
                cached_data, cached_at = cached
                if time.time() - cached_at < self._ohlcv_cache_ttl:
                    return cached_data

        await self._ensure_pair_cache()
        last_error = None
        max_attempts = 3
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
                        "1m": ("1min", 1), "5m": ("5min", 5), "15m": ("15min", 15), "30m": ("30min", 30),
                        "1h": ("1h", 60), "2h": ("2h", 120), "4h": ("4h", 240), "6h": ("6h", 360),
                        "8h": ("8h", 480), "12h": ("12h", 720), "1d": ("1d", 1440), "3d": ("3d", 4320), "1w": ("1w", 10080),
                    }
                    pd_label, agg = aggregation_map.get(timeframe, ("1h", 60))

                    base_limit = {"1m": 1000, "15m": 1000, "1h": 1000, "1d": 1000}.get(resolution, 1000)
                    fetch_limit = min(int(limit * max(agg / 60, 1) * 1.5), base_limit)

                    params = {"pair": pair, "interval": resolution, "limit": fetch_limit}
                    if start_time is not None:
                        params["startTime"] = start_time
                    if end_time is not None:
                        params["endTime"] = end_time

                    resp = await http.get(
                        f"https://public.coindcx.com/market_data/candles",
                        params=params, timeout=httpx.Timeout(20.0, connect=15.0),
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
                        if start_time is None and end_time is None:
                            self._ohlcv_cache[cache_key] = (ohlcv, time.time())
                        return ohlcv
                    if resp.status_code != 200:
                        logger.warning(f"OHLCV fetch for {symbol} returned HTTP {resp.status_code}")
                    return []
                except httpx.ConnectError as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        logger.warning(f"Failed to fetch OHLCV for {symbol}: {e}")
                        return []
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        logger.warning(f"Failed to fetch OHLCV for {symbol}: {e}")
                        return []

    async def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        for attempt in range(2):
            async with self._rate_limiter:
                await self._rate_limit()
                try:
                    http = await self._get_http()
                    pair = self._get_coin_dcx_pair(symbol)
                    resp = await http.get(
                        f"{self.base_url}/exchange/v1/derivatives/futures/ticker",
                        params={"pair": pair},
                        timeout=httpx.Timeout(15.0, connect=10.0),
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
                except (httpx.ConnectError, httpx.TimeoutException) as e:
                    if attempt == 0:
                        await asyncio.sleep(1)
                        continue
                    logger.debug(f"Failed to fetch ticker for {symbol}: {e}")
                    return None
                except Exception as e:
                    logger.debug(f"Failed to fetch ticker for {symbol}: {e}")
                    return None

    async def fetch_all_tickers(self, quote_currency: str = "USDT") -> Dict[str, Dict]:
        max_retries = 3
        last_error = None
        for attempt in range(max_retries):
            try:
                async with self._rate_limiter:
                    await self._rate_limit()
                    http = await self._get_http()
                    resp = await http.get(
                        f"{self.base_url}/exchange/ticker",
                        timeout=httpx.Timeout(30.0, connect=15.0),
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if not data:
                            logger.warning(f"fetch_all_tickers attempt {attempt+1}/{max_retries}: empty response")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            return {}
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
                    elif resp.status_code in (429, 502, 503):
                        logger.warning(f"fetch_all_tickers attempt {attempt+1}/{max_retries}: HTTP {resp.status_code}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                    else:
                        logger.warning(f"fetch_all_tickers attempt {attempt+1}/{max_retries}: unexpected HTTP {resp.status_code}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                    return {}
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError) as e:
                last_error = f"{type(e).__name__}: {e}"
                logger.warning(f"fetch_all_tickers attempt {attempt+1}/{max_retries}: {last_error}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                break
            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                logger.error(f"Failed to fetch all tickers: {last_error}")
                break

        logger.warning(f"Fetching individual tickers for {len(FALLBACK_SYMBOLS)} fallback symbols")
        return await self._fetch_fallback_tickers(quote_currency)

    async def _fetch_fallback_tickers(self, quote_currency: str = "USDT") -> Dict[str, Dict]:
        tickers = {}
        sem = asyncio.Semaphore(5)
        async def _fetch(symbol):
            async with sem:
                ticker = await self.fetch_ticker(symbol)
                if ticker:
                    return symbol, ticker
                return None
        results = await asyncio.gather(*[_fetch(s) for s in FALLBACK_SYMBOLS])
        for r in results:
            if r:
                sym, t = r
                tickers[sym] = t
        if tickers:
            logger.info(f"Fetched {len(tickers)} tickers via fallback individual requests")
        return tickers

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
                           amount: float, price: Optional[float] = None,
                           leverage: Optional[int] = None) -> Optional[Dict]:
        if not self.api_key or not self.api_secret:
            return {"message": "API keys not configured"}
        if leverage and settings.bot_mode == "live":
            await self.set_leverage(symbol, leverage)
        async with self._rate_limiter:
            await self._rate_limit()
            try:
                http = await self._get_http()
                await self._ensure_pair_cache()
                pair = self._get_coin_dcx_pair(symbol)
                payload = {
                    "side": side.upper(),
                    "order_type": order_type.upper(),
                    "market": pair,
                    "price_per_unit": price or 0,
                    "total_quantity": amount,
                    "timestamp": int(time.time() * 1000),
                }
                headers = self._sign_request(payload)
                endpoint = f"{self.base_url}/exchange/v1/orders/create"
                if settings.bot_mode == "live":
                    endpoint = f"{self.base_url}/exchange/v1/derivatives/futures/orders/create"
                resp = await http.post(
                    endpoint, headers=headers, data=json.dumps(payload),
                )
                if resp.status_code == 200:
                    return resp.json()
                logger.error(f"Order failed for {symbol}: {resp.status_code} {resp.text}")
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

    async def fetch_order(self, order_id: str, symbol: str) -> Optional[Dict]:
        if not self.api_key or not self.api_secret:
            return None
        async with self._rate_limiter:
            await self._rate_limit()
            try:
                open_orders = await self.fetch_open_orders(symbol)
                for o in open_orders:
                    if o.get("id") == order_id:
                        return o
                try:
                    http = await self._get_http()
                    payload = {"id": order_id, "timestamp": int(time.time() * 1000)}
                    headers = self._sign_request(payload)
                    resp = await http.post(
                        f"{self.base_url}/exchange/v1/orders/status",
                        headers=headers, data=json.dumps(payload),
                    )
                    if resp.status_code == 200:
                        return resp.json()
                except Exception:
                    pass
                return None
            except Exception as e:
                logger.error(f"Failed to fetch order {order_id}: {e}")
                return None

    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        if not self.api_key or not self.api_secret or settings.bot_mode != "live":
            return True
        async with self._rate_limiter:
            await self._rate_limit()
            try:
                http = await self._get_http()
                await self._ensure_pair_cache()
                pair = self._get_coin_dcx_pair(symbol)
                payload = {
                    "market": pair,
                    "leverage": leverage,
                    "timestamp": int(time.time() * 1000),
                    "side": "both",
                }
                headers = self._sign_request(payload)
                resp = await http.post(
                    f"{self.base_url}/exchange/v1/derivatives/futures/orders/set_leverage",
                    headers=headers, data=json.dumps(payload),
                )
                if resp.status_code == 200:
                    logger.info(f"Leverage set to {leverage}x for {symbol}")
                    return True
                logger.warning(f"Failed to set leverage for {symbol}: {resp.status_code} {resp.text}")
                return False
            except Exception as e:
                logger.error(f"Failed to set leverage: {e}")
                return False

    async def fetch_positions(self) -> List[Dict]:
        if not self.api_key or not self.api_secret:
            return []
        async with self._rate_limiter:
            await self._rate_limit()
            try:
                http = await self._get_http()
                payload = {"timestamp": int(time.time() * 1000)}
                headers = self._sign_request(payload)
                resp = await http.post(
                    f"{self.base_url}/exchange/v1/derivatives/futures/positions",
                    headers=headers, data=json.dumps(payload),
                )
                if resp.status_code == 200:
                    return resp.json()
                return []
            except Exception as e:
                logger.error(f"Failed to fetch positions: {e}")
                return []

    async def check_exchange_status(self) -> bool:
        try:
            http = await self._get_http()
            resp = await asyncio.wait_for(
                http.get(f"{self.base_url}/exchange/v1/markets", timeout=5),
                timeout=5,
            )
            return resp.status_code == 200
        except Exception:
            return False

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
