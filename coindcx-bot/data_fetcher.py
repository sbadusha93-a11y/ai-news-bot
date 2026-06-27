import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://api.coindcx.com"
PUBLIC = "https://public.coindcx.com"

session = requests.Session()
session.headers.update({"User-Agent": "CoindcxBot/1.0"})


def api_get(url, params=None, retries=2):
    for i in range(retries):
        try:
            r = session.get(url, params=params, timeout=8)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(0.5)


def to_candle_pair(ticker_pair):
    for quote in ["USDT", "INR", "BTC", "ETH", "USDC"]:
        if ticker_pair.endswith(quote) and len(ticker_pair) > len(quote):
            base = ticker_pair[: -len(quote)]
            return f"B-{base}_{quote}"
    return f"B-{ticker_pair}"


def from_candle_pair(candle_pair):
    s = candle_pair.replace("B-", "")
    parts = s.split("_")
    return parts[0]


def get_markets():
    return api_get(f"{BASE}/exchange/v1/markets")


def get_ticker():
    return api_get(f"{BASE}/exchange/ticker")


def get_candles(pair, interval="4h", limit=500):
    params = {"pair": pair, "interval": interval, "limit": limit}
    return api_get(f"{PUBLIC}/market_data/candles", params)


def get_top_usdt_pairs(top_n=10):
    ticker = get_ticker()
    usdt = [t for t in ticker if t.get("market", "").endswith("USDT")]
    usdt.sort(key=lambda x: abs(float(x.get("volume", 0))), reverse=True)
    return usdt[:top_n]


def fetch_all_candles(pairs, interval="4h", limit=500):
    result = {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {}
        for p in pairs:
            candle_pair = to_candle_pair(p["market"])
            futures[ex.submit(get_candles, candle_pair, interval, limit)] = p["market"]
        for f in as_completed(futures):
            ticker_pair = futures[f]
            try:
                result[ticker_pair] = f.result()
            except Exception:
                result[ticker_pair] = None
    return result


def fetch_btc_candles(interval="4h", limit=500):
    return get_candles("B-BTC_USDT", interval, limit)
