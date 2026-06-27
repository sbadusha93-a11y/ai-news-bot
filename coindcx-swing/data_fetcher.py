import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://api.coindcx.com"
PUBLIC = "https://public.coindcx.com"

session = requests.Session()
session.headers.update({"User-Agent": "CoindcxSwing/1.0"})


def api_get(url, params=None, retries=2):
    for i in range(retries):
        try:
            r = session.get(url, params=params, timeout=8)
            r.raise_for_status()
            return r.json()
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(0.5)


def to_candle_pair(ticker_pair):
    for quote in ["USDT", "INR", "BTC", "ETH", "USDC"]:
        if ticker_pair.endswith(quote) and len(ticker_pair) > len(quote):
            base = ticker_pair[:-len(quote)]
            return f"B-{base}_{quote}"
    return f"B-{ticker_pair}"


def from_candle_pair(candle_pair):
    s = candle_pair.replace("B-", "")
    parts = s.split("_")
    return parts[0]


def get_ticker():
    return api_get(f"{BASE}/exchange/ticker")


def get_candles(pair, interval="1h", limit=500):
    params = {"pair": pair, "interval": interval, "limit": limit}
    return api_get(f"{PUBLIC}/market_data/candles", params)


def get_top_usdt_pairs(top_n=10):
    ticker = get_ticker()
    usdt = [t for t in ticker if t.get("market", "").endswith("USDT")]
    usdt.sort(key=lambda x: abs(float(x.get("volume", 0))), reverse=True)
    return usdt[:top_n]


def fetch_all_candles(pairs, interval="1h", limit=500):
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


def get_top_futures_pairs(top_n=10, extra_symbols=None):
    instruments = api_get(
        f"{BASE}/exchange/v1/derivatives/futures/data/active_instruments",
        {"margin_currency_short_name[]": "USDT"},
    )
    usdt = [s for s in instruments if s.endswith("_USDT")]
    ticker_all = get_ticker()
    vol_map = {}
    for t in ticker_all:
        m = t.get("market", "")
        vol_map[m] = abs(float(t.get("volume", 0)))
    def vol_key(pair_str):
        base = pair_str.replace("B-", "").replace("_", "")
        return vol_map.get(base, 0)
    usdt.sort(key=vol_key, reverse=True)
    seen = set()
    result = []
    for s in usdt:
        market_name = s.replace("B-", "").replace("_", "")
        if market_name not in seen:
            seen.add(market_name)
            result.append({"market": market_name})
    if extra_symbols:
        for sym in extra_symbols:
            m = sym.upper().replace(" ", "")
            if not m.endswith("USDT"):
                m += "USDT"
            candle = f"B-{m[:-4]}_{m[-4:]}"
            if candle in instruments:
                entry = {"market": m}
                if entry in result:
                    result.remove(entry)
                result.insert(0, entry)
    return result[:top_n]


def fetch_btc_candles(interval="1h", limit=500):
    return get_candles("B-BTC_USDT", interval, limit)
