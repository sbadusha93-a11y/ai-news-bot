import requests
import time
from functools import lru_cache

_COINGECKO = "https://api.coingecko.com/api/v3"
_session = requests.Session()
_session.headers.update({"User-Agent": "CoindcxBot/1.0", "Accept": "application/json"})
_last_fetch = 0
_cache_ttl = 120

_fundamental_cache = {}


def _rate_limited_get(url, params=None, retries=2):
    global _last_fetch
    for i in range(retries):
        elapsed = time.time() - _last_fetch
        if elapsed < 1.5:
            time.sleep(1.5 - elapsed)
        try:
            _last_fetch = time.time()
            r = _session.get(url, params=params, timeout=8)
            if r.status_code == 429:
                time.sleep(5)
                continue
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()
        except Exception:
            if i == retries - 1:
                return None
            time.sleep(1)


def _needs_refresh():
    now = time.time()
    for k, (ts, _) in list(_fundamental_cache.items()):
        if now - ts > _cache_ttl:
            del _fundamental_cache[k]
    return _fundamental_cache


def fetch_fundamentals(coin_symbols):
    coin_symbols = list(set(c.lower() for c in coin_symbols if c))
    fetched = {}
    cached = {}

    for sym in coin_symbols:
        if sym in _fundamental_cache:
            ts, data = _fundamental_cache[sym]
            if time.time() - ts < _cache_ttl:
                cached[sym] = data
                continue

    remaining = [s for s in coin_symbols if s not in cached]
    if remaining:
        market_data = _rate_limited_get(
            f"{_COINGECKO}/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "24h,7d",
            },
        )
        if market_data:
            coin_map = {}
            for c in market_data:
                sym = c.get("symbol", "").lower()
                coin_map[sym] = c

            for sym in remaining:
                entry = coin_map.get(sym)
                if entry:
                    result = {
                        "rank": entry.get("market_cap_rank"),
                        "market_cap": entry.get("market_cap"),
                        "total_volume": entry.get("total_volume"),
                        "circulating_supply": entry.get("circulating_supply"),
                        "total_supply": entry.get("total_supply"),
                        "max_supply": entry.get("max_supply"),
                        "ath": entry.get("ath"),
                        "atl": entry.get("atl"),
                        "price_change_24h": entry.get("price_change_percentage_24h"),
                        "price_change_7d": entry.get("price_change_percentage_7d_in_currency"),
                        "high_24h": entry.get("high_24h"),
                        "low_24h": entry.get("low_24h"),
                    }
                    _fundamental_cache[sym] = (time.time(), result)
                    fetched[sym] = result
                else:
                    _fundamental_cache[sym] = (time.time(), None)
                    fetched[sym] = None
        else:
            for sym in remaining:
                fetched[sym] = None

    return {**cached, **fetched}


def _to_num(val):
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def score_fundamentals(data, price):
    if not data:
        return 0, {}

    checks = {}
    score = 0
    price = _to_num(price) or 0

    rank = data.get("rank")
    rank = _to_num(rank)
    if rank is not None:
        if rank <= 50:
            checks["Top50"] = True
            score += 1
        elif rank <= 100:
            checks["Top100"] = True
            score += 1
        else:
            checks["Rank"] = False

    mcap = _to_num(data.get("market_cap"))
    volume = _to_num(data.get("total_volume"))
    if mcap and volume and mcap > 0:
        vol_mcap_ratio = volume / mcap
        if vol_mcap_ratio > 0.15:
            checks["Liq"] = True
            score += 1
        elif vol_mcap_ratio > 0.05:
            checks["LiqOk"] = True
        else:
            checks["LiqLow"] = True

    change_7d = _to_num(data.get("price_change_7d"))
    if change_7d is not None:
        if change_7d > 10:
            checks["7dMomo"] = True
            score += 1
        elif change_7d > 0:
            checks["7dUp"] = True
        elif change_7d < -15:
            checks["7dCrash"] = True
        else:
            checks["7dDown"] = True

    cs = _to_num(data.get("circulating_supply"))
    ms = _to_num(data.get("max_supply"))
    if cs and ms and ms > 0:
        inflation = 1 - (cs / ms)
        if inflation > 0.2:
            checks["Room"] = True
            score += 1
        else:
            checks["FullDil"] = True

    ath = _to_num(data.get("ath"))
    if ath and price and ath > 0:
        dist_from_ath = ((ath - price) / ath) * 100
        if dist_from_ath > 70:
            checks["Dip"] = True
            score += 1

    return score, checks
