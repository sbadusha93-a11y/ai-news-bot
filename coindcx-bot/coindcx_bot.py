import sys
import os
import time
import traceback
from datetime import datetime, timedelta, timezone
from rich.console import Console
from rich.table import Table
from rich import box

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import data_fetcher as df
import indicators as ind
import scorer as sc
import fundamentals as fund
import numpy as np
from display import LiveDisplay
import dashboard
import trader

console = Console()
_ticker_cache = {}
_sl_cooldown = {}
SL_COOLDOWN_HOURS = 24


def _fmt(p):
    if p >= 100: return f"{p:.2f}"
    if p >= 10: return f"{p:.3f}"
    if p >= 1: return f"{p:.4f}"
    if p >= 0.01: return f"{p:.5f}"
    return f"{p:.6f}"


def _fetch_ticker_data(pairs):
    global _ticker_cache
    try:
        ticker_all = df.get_ticker()
        prices = {}
        changes = {}
        for p in pairs:
            market = p["market"]
            coin = df.from_candle_pair(df.to_candle_pair(market))
            for t in ticker_all:
                if t.get("market") == market:
                    prices[coin] = float(t.get("last_price", 0))
                    chg = t.get("change_24_hour")
                    changes[coin] = float(chg) if chg else None
                    break
        _ticker_cache = changes
        dashboard.update_live_prices(prices)
        return prices, changes
    except Exception:
        return {}, {}


def time_to_candle_close(interval_minutes):
    now = datetime.now(timezone.utc)
    total_mins = now.hour * 60 + now.minute
    current_block = (total_mins // interval_minutes) * interval_minutes
    next_block = current_block + interval_minutes
    if next_block >= 1440:
        next_dt = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        h = int(next_block // 60)
        m = int(next_block % 60)
        next_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
    secs = max(0, (next_dt - now).total_seconds())
    hh = int(secs // 3600)
    mm = int((secs % 3600) // 60)
    ss = int(secs % 60)
    return f"{hh}:{mm:02d}:{ss:02d}", int(secs)


def suggest_leverage(atr_val, price):
    if price <= 0 or atr_val <= 0:
        return "3x"
    atr_pct = (atr_val / price) * 100
    if atr_pct > 3.0:
        return "2x"
    elif atr_pct > 1.5:
        return "3x"
    else:
        return "5x"


def compute_indicators(closes, highs, lows, volumes):
    if len(closes) < 200:
        return None
    ema20_arr = ind.ema(closes, 20)
    ema50_arr = ind.ema(closes, 50)
    ema200_arr = ind.ema(closes, 200)
    vwap_arr = ind.vwap(highs, lows, closes, volumes)
    rsi_arr = ind.rsi(closes, 14)
    macd_line, sig_line, macd_hist = ind.macd(closes)
    sk_arr, sd_arr = ind.stoch_rsi(closes)
    atr_arr = ind.atr(highs, lows, closes)
    high_10_arr = ind.highest(highs, 10)
    low_10_arr = ind.lowest(lows, 10)
    vol_sma_arr = ind.volume_sma(volumes, 20)
    return {
        "ema20": ema20_arr,
        "ema50": ema50_arr,
        "ema200": ema200_arr,
        "vwap": vwap_arr,
        "rsi": rsi_arr,
        "macd_line": macd_line,
        "sig_line": sig_line,
        "macd_hist": macd_hist,
        "sk": sk_arr,
        "sd": sd_arr,
        "atr": atr_arr,
        "high_10": high_10_arr,
        "low_10": low_10_arr,
        "vol_sma": vol_sma_arr,
    }


def extract_candle_arrays(candle_data):
    candles = candle_data[::-1]
    closes = np.array([float(c["close"]) for c in candles], dtype=float)
    highs = np.array([float(c["high"]) for c in candles], dtype=float)
    lows = np.array([float(c["low"]) for c in candles], dtype=float)
    volumes = np.array([float(c["volume"]) for c in candles], dtype=float)
    return candles, closes, highs, lows, volumes


def calc_deepseek_confidence(r, btc_trend):
    score = 0
    dir_ = r.get("direction")
    long_pct = r.get("long_pct") or 0
    short_pct = r.get("short_pct") or 0
    checks = r.get("checks") or {}

    # Signal strength (40%)
    max_score = max(long_pct, short_pct)
    score += max_score * 0.4

    # Check pass rate (15%)
    total = len(checks)
    passed = sum(1 for v in checks.values() if v)
    pass_rate = (passed / total * 100) if total > 0 else 0
    score += pass_rate * 0.15

    # BTC trend alignment (10%)
    if btc_trend == "bullish" and dir_ == "LONG":
        score += 10
    elif btc_trend == "bearish" and dir_ == "SHORT":
        score += 10
    elif btc_trend == "neutral":
        score += 5

    # Fundamentals (10%)
    fund_pct = r.get("fund_pct") or 0
    score += fund_pct * 0.10

    # RSI sweet spot (10%)
    rsi = r.get("rsi")
    if rsi is not None:
        if dir_ == "LONG" and 50 <= rsi <= 70:
            score += 10
        elif dir_ == "SHORT" and 30 <= rsi <= 50:
            score += 10
        elif rsi < 20 or rsi > 80:
            score += 5
        else:
            score += 3

    # Risk/reward quality (10%)
    rr = r.get("rr") or 0
    if rr >= 3: score += 10
    elif rr >= 2: score += 8
    elif rr >= 1.5: score += 5
    else: score += 2

    # Volatility check (5%)
    atr = r.get("atr_pct") or 0
    if 0.5 <= atr <= 5: score += 5
    elif atr > 0: score += 2

    return round(min(score, 99), 0)


def compute_ds_score_from_1h(candle_1h, coin_name, btc_trend, fund_data=None):
    try:
        if not candle_1h or len(candle_1h) < 100:
            return 0
        candles, closes, highs, lows, volumes = extract_candle_arrays(candle_1h)
        latest = candles[-1]
        price = float(latest["close"])
        if (time.time() - float(latest["time"]) / 1000) / 3600 > 24:
            return 0

        indicators = compute_indicators(closes, highs, lows, volumes)
        if indicators is None:
            return 0

        ema20 = indicators["ema20"][-1]
        ema50 = indicators["ema50"][-1]
        ema200 = indicators["ema200"][-1]
        vwap = indicators["vwap"][-1]
        rsi_val = indicators["rsi"][-1]
        macd_line = indicators["macd_line"][-1]
        sig_line = indicators["sig_line"][-1]
        macd_hist = indicators["macd_hist"][-1]
        sk = indicators["sk"][-1]
        sd = indicators["sd"][-1]
        sk_prev = indicators["sk"][-2]
        sd_prev = indicators["sd"][-2]
        atr_val = indicators["atr"][-1]
        high_10 = indicators["high_10"][-1]
        low_10 = indicators["low_10"][-1]

        curr_candle = candles[-1]
        prev_candle = candles[-2]
        patterns = ind.detect_candle_pattern(
            float(curr_candle["open"]), float(curr_candle["high"]),
            float(curr_candle["low"]), float(curr_candle["close"]),
            float(prev_candle["open"]), float(prev_candle["high"]),
            float(prev_candle["low"]), float(prev_candle["close"]),
        )

        vol_sma = indicators["vol_sma"][-1]
        vol_latest = float(candles[-1]["volume"]) if len(candles) > 0 else 0
        fund_raw = (fund_data or {}).get(coin_name.lower())
        fund_score, fund_checks = fund.score_fundamentals(fund_raw, price) if fund_raw else (0, {})
        fund_pct = min(round(fund_score / 5 * 100, 1), 100) if fund_raw else 0

        signal, direction, checks, long_pct, short_pct, pump_flag, pump_ratio = sc.get_signal(
            price, vwap, ema20, ema50, ema200, rsi_val,
            macd_line, sig_line, macd_hist,
            sk, sd, sk_prev, sd_prev,
            patterns, btc_trend, fund_score, fund_checks,
            vol_latest, vol_sma, high_10, low_10,
        )

        show_dir = direction if direction in ("LONG", "SHORT") else ("LONG" if long_pct >= short_pct else "SHORT")
        entry = sc.calculate_entry(
            float(candles[-1]["high"]), float(candles[-1]["low"]), price,
            high_10, low_10, show_dir,
        )
        target, sl, rr = sc.calculate_target_sl(entry, atr_val, high_10, low_10, ema20, show_dir)
        atr_pct = round((atr_val / price) * 100, 2) if atr_val and price > 0 else 0

        ds_input = {
            "direction": direction,
            "long_pct": long_pct,
            "short_pct": short_pct,
            "checks": checks or {},
            "fund_pct": fund_pct,
            "rsi": round(rsi_val, 1) if rsi_val else None,
            "rr": rr or 0,
            "atr_pct": atr_pct,
        }
        return calc_deepseek_confidence(ds_input, btc_trend)
    except Exception:
        return 0


def get_btc_trend(interval="1h", limit=500):
    try:
        btc_candles = df.fetch_btc_candles(interval, limit)
        if not btc_candles or len(btc_candles) < 100:
            return "neutral"
        _, btc_closes, btc_highs, btc_lows, btc_volumes = extract_candle_arrays(btc_candles)
        if len(btc_closes) < 100:
            return "neutral"
        btc_ema20 = ind.ema(btc_closes, 20)[-1]
        btc_ema50 = ind.ema(btc_closes, 50)[-1]
        btc_vwap = ind.vwap(btc_highs, btc_lows, btc_closes, btc_volumes)[-1]
        btc_price = btc_closes[-1]
        if btc_price > btc_vwap and btc_ema20 > btc_ema50:
            return "bullish"
        elif btc_price < btc_vwap and btc_ema20 < btc_ema50:
            return "bearish"
        else:
            return "neutral"
    except Exception:
        return "neutral"


def analyze_coin(candle_data, coin_name, btc_trend, fund_data=None):
    try:
        if not candle_data or len(candle_data) < 200:
            return None

        candles, closes, highs, lows, volumes = extract_candle_arrays(candle_data)
        latest = candles[-1]
        price = float(latest["close"])
        candle_time = float(latest["time"]) / 1000
        age_hours = (time.time() - candle_time) / 3600
        if age_hours > 12:
            return None

        indicators = compute_indicators(closes, highs, lows, volumes)
        if indicators is None:
            return None

        ema20 = indicators["ema20"][-1]
        ema50 = indicators["ema50"][-1]
        ema200 = indicators["ema200"][-1]
        vwap = indicators["vwap"][-1]
        rsi_val = indicators["rsi"][-1]
        macd_line = indicators["macd_line"][-1]
        sig_line = indicators["sig_line"][-1]
        macd_hist = indicators["macd_hist"][-1]
        sk = indicators["sk"][-1]
        sd = indicators["sd"][-1]
        sk_prev = indicators["sk"][-2]
        sd_prev = indicators["sd"][-2]
        atr_val = indicators["atr"][-1]
        high_10 = indicators["high_10"][-1]
        low_10 = indicators["low_10"][-1]

        curr_candle = candles[-1]
        prev_candle = candles[-2]
        patterns = ind.detect_candle_pattern(
            float(curr_candle["open"]),
            float(curr_candle["high"]),
            float(curr_candle["low"]),
            float(curr_candle["close"]),
            float(prev_candle["open"]),
            float(prev_candle["high"]),
            float(prev_candle["low"]),
            float(prev_candle["close"]),
        )

        vol_sma = indicators["vol_sma"][-1]
        vol_latest = float(candles[-1]["volume"]) if len(candles) > 0 else 0
        fund_raw = (fund_data or {}).get(coin_name.lower())
        fund_score, fund_checks = fund.score_fundamentals(fund_raw, price) if fund_raw else (0, {})
        fund_pct = min(round(fund_score / 5 * 100, 1), 100) if fund_raw else 0

        signal, direction, checks, long_pct, short_pct, pump_flag, pump_ratio = sc.get_signal(
            price, vwap, ema20, ema50, ema200, rsi_val,
            macd_line, sig_line, macd_hist,
            sk, sd, sk_prev, sd_prev,
            patterns, btc_trend, fund_score, fund_checks,
            vol_latest, vol_sma, high_10, low_10,
        )

        show_dir = direction if direction in ("LONG", "SHORT") else ("LONG" if long_pct >= short_pct else "SHORT")
        entry = sc.calculate_entry(
            float(latest["high"]), float(latest["low"]), price,
            high_10, low_10, show_dir,
        )
        target, sl, rr = sc.calculate_target_sl(entry, atr_val, high_10, low_10, ema20, show_dir)

        leverage = suggest_leverage(atr_val, price) if atr_val else "3x"
        atr_pct = round((atr_val / price) * 100, 2) if atr_val and price > 0 else 0
        vol_latest = float(candles[-1]["volume"]) if len(candles) > 0 else 0
        change_24h = _ticker_cache.get(coin_name)
        rsi_val_display = round(rsi_val, 1) if rsi_val else None

        return {
            "ds_conf": 0,
            "coin": coin_name,
            "price": price,
            "direction": direction,
            "entry": entry,
            "entry_dir": show_dir,
            "target": target,
            "sl": sl,
            "rr": rr or 0,
            "leverage": leverage,
            "checks": checks,
            "long_pct": long_pct,
            "short_pct": short_pct,
            "fund_pct": fund_pct,
            "atr_pct": atr_pct,
            "rsi": rsi_val_display,
            "volume": vol_latest,
            "change_24h": change_24h,
            "pump": pump_flag,
            "pump_ratio": pump_ratio,
            "ema20": round(ema20, 6) if ema20 else None,
            "ema50": round(ema50, 6) if ema50 else None,
            "ema200": round(ema200, 6) if ema200 else None,
            "vwap": round(vwap, 6) if vwap else None,
        }
    except Exception as e:
        console.print(f"[red]Error analyzing {coin_name}: {e}[/red]")
        return None


def check_trend(candle_data):
    if not candle_data or len(candle_data) < 100:
        return None
    try:
        candles, closes, highs, lows, volumes = extract_candle_arrays(candle_data)
        price = closes[-1]
        vwap = ind.vwap(highs, lows, closes, volumes, period=20)[-1]
        ema20 = ind.ema(closes, 20)[-1]
        ema50 = ind.ema(closes, 50)[-1]
        ema200 = ind.ema(closes, 200)[-1]
        adx_arr, plus_di, minus_di = ind.adx(highs, lows, closes)
        adx_val = adx_arr[-1] if not np.isnan(adx_arr[-1]) else 0
        if adx_val < 20:
            return None
        if price > vwap and ema20 > ema50 > ema200:
            return "LONG"
        if price < vwap and ema20 < ema50 < ema200:
            return "SHORT"
    except Exception:
        pass
    return None


def check_momentum(candle_data, direction):
    if not candle_data or len(candle_data) < 50:
        return False
    try:
        candles, closes, highs, lows, volumes = extract_candle_arrays(candle_data)
        rsi_arr = ind.rsi(closes, 14)
        macd_line, sig_line, _ = ind.macd(closes)
        rsi_val = rsi_arr[-1]
        if direction == "LONG":
            return rsi_val > 50 and macd_line[-1] > sig_line[-1]
        else:
            return rsi_val < 50 and macd_line[-1] < sig_line[-1]
    except Exception:
        return False


def main():
    global _sl_cooldown
    try:
        display = LiveDisplay()
        console.print("[bold cyan]CoinDCX Signal Scanner[/bold cyan]")
        dashboard.start()
        dashboard._data["stats"] = {"btc_trend": "neutral", "next_candle": "-", "signals": 0, "mode": "OFF"}
        trader.load_config(os.path.join(BASE_DIR, "config.json"))
        if trader.is_trading_enabled():
            mode = "PAPER" if trader.is_paper_mode() else "LIVE"
            console.print(f"[yellow]Auto-trade ENABLED ({mode})[/yellow]")
        else:
            console.print("[dim]Auto-trade DISABLED (configure config.json)[/dim]")
        console.print(f"[green]Dashboard: http://{dashboard._host}:{dashboard._port}[/green]")
        console.print("Checking...")

        pairs = df.get_top_usdt_pairs(50)
        if not pairs:
            console.print("[red]No USDT pairs found[/red]")
            return

        coin_names = [df.from_candle_pair(df.to_candle_pair(p["market"])) for p in pairs]
        console.print(f"Scanning {len(pairs)} coins for signals (may take 15-30s on first run)...")

        last_scan_time = 0
        last_trend_fetch = -99999
        last_mom_fetch = -99999
        candles_trend_map = {}
        candles_mom_map = {}
        ds_scores = {}
        signal_history = {}
        locked = {}
        live_prices = {}

        while True:
            try:
                candle_str, secs_left = time_to_candle_close(15)
                now = time.time()

                btc_trend = get_btc_trend("1h", 500)

                live_prices, _ = _fetch_ticker_data(pairs)

                if now - last_scan_time >= 30:
                    last_scan_time = now

                    _needs_trend = not candles_trend_map
                    if not _needs_trend and (now - last_trend_fetch) >= 300:
                        _ref = candles_trend_map.get(pairs[0]["market"])
                        if _ref and len(_ref) > 0:
                            _t = float(_ref[-1]["time"])
                            _needs_trend = (now * 1000) >= (_t + 3600 * 1000)
                        _needs_trend = _needs_trend or (now - last_trend_fetch >= 7200)
                    if _needs_trend:
                        last_trend_fetch = now
                        candles_trend_map = df.fetch_all_candles(pairs, "1h", 200)
                    if now - last_mom_fetch >= 900 or not candles_mom_map:
                        last_mom_fetch = now
                        candles_mom_map = df.fetch_all_candles(pairs, "15m", 100)
                        candles_map = df.fetch_all_candles(pairs, "15m", 1000)

                    coin_names_lower = [c.lower() for c in coin_names]
                    fund_data = fund.fetch_fundamentals(coin_names_lower)

                    rows = []
                    now_clean = time.time()
                    _sl_cooldown = {k: v for k, v in _sl_cooldown.items() if now_clean - v < SL_COOLDOWN_HOURS * 3600}
                    for p in pairs:
                        coin_name = df.from_candle_pair(df.to_candle_pair(p["market"]))
                        if coin_name in _sl_cooldown:
                            continue
                        candle_trend = candles_trend_map.get(p["market"])
                        candle_mom = candles_mom_map.get(p["market"])
                        trend_dir = check_trend(candle_trend)
                        has_momentum = trend_dir and check_momentum(candle_mom, trend_dir)
                        candle_data = candles_map.get(p["market"])
                        result = analyze_coin(candle_data, coin_name, btc_trend, fund_data)
                        if result:
                            if not (has_momentum and result.get("direction") == trend_dir):
                                result["direction"] = "NONE"
                            rows.append(result)
                            ds_scores[coin_name] = compute_ds_score_from_1h(candle_trend, coin_name, btc_trend, fund_data)

                    display_rows = []
                    for r in rows:
                        coin = r["coin"]
                        pos = trader._open_positions.get(coin)
                        ds_val = ds_scores.get(coin)
                        r["ds_conf"] = ds_val if ds_val else calc_deepseek_confidence(r, btc_trend)
                        raw_dir = r.get("direction", "NONE")
                        prev = signal_history.get(coin, {"dir": None, "count": 0, "stable": "NONE"})
                        is_new_trend = now - last_trend_fetch < 60
                        if is_new_trend:
                            if prev["dir"] == raw_dir:
                                signal_history[coin] = {"dir": raw_dir, "count": prev["count"] + 1, "stable": prev["stable"]}
                            else:
                                signal_history[coin] = {"dir": raw_dir, "count": 1, "stable": prev["stable"]}
                            if signal_history[coin]["count"] >= 3:
                                signal_history[coin]["stable"] = raw_dir
                        else:
                            signal_history[coin] = {"dir": raw_dir, "count": 1, "stable": raw_dir}
                        r["direction"] = signal_history[coin]["stable"]
                        r["persist"] = signal_history[coin]["count"]
                        r["prev_dir"] = raw_dir

                        if r["direction"] in ("LONG", "SHORT") or (r["direction"] == "NONE" and r.get("ds_conf", 0) >= 75):
                            dir_ = r["direction"] if r["direction"] in ("LONG", "SHORT") else ("LONG" if (r.get("long_pct") or 0) >= (r.get("short_pct") or 0) else "SHORT")
                            lk = locked.get(coin)
                            if lk and lk["dir"] == dir_:
                                for k in ("entry", "target", "sl", "rr", "ds_conf", "long_pct", "short_pct", "fund_pct", "atr_pct", "rsi", "volume", "pump", "pump_ratio", "leverage"):
                                    if k in lk:
                                        r[k] = lk[k]
                            else:
                                locked[coin] = {"dir": dir_, "entry": r["entry"], "target": r["target"], "sl": r["sl"],
                                    "rr": r.get("rr"), "ds_conf": r.get("ds_conf", 0),
                                    "long_pct": r.get("long_pct"), "short_pct": r.get("short_pct"),
                                    "fund_pct": r.get("fund_pct"), "atr_pct": r.get("atr_pct"),
                                    "rsi": r.get("rsi"), "volume": r.get("volume", 0),
                                    "pump": r.get("pump", False), "pump_ratio": r.get("pump_ratio", 0),
                                    "leverage": r.get("leverage")}
                            display_rows.append(r)
                        elif pos:
                            display_rows.append({
                                "coin": coin,
                                "price": r.get("price") or pos["entry"],
                                "direction": pos["direction"],
                                "entry": pos["entry"],
                                "target": pos["target"],
                                "sl": pos["sl"],
                                "rr": abs((pos["target"] - pos["entry"]) / (pos["entry"] - pos["sl"] + 1e-10)) if pos["direction"] == "LONG" else abs((pos["entry"] - pos["target"]) / (pos["sl"] - pos["entry"] + 1e-10)),
                                "leverage": "POS",
                                "long_pct": r.get("long_pct"),
                                "short_pct": r.get("short_pct"),
                                "fund_pct": r.get("fund_pct"),
                                "atr_pct": r.get("atr_pct"),
                                "rsi": r.get("rsi"),
                                "volume": r.get("volume", 0),
                                "change_24h": r.get("change_24h"),
                                "ds_conf": r.get("ds_conf", 0),
                                "persist": r.get("persist", 0),
                                "pump": r.get("pump", False),
                                "pump_ratio": r.get("pump_ratio", 0),
                            })
                        else:
                            display_rows.append({
                                "coin": coin,
                                "price": r.get("price") or 0,
                                "direction": "NONE",
                                "entry": r.get("entry"),
                                "target": r.get("target"),
                                "sl": r.get("sl"),
                                "rr": r.get("rr", 0) or 0,
                                "leverage": r.get("leverage", "-"),
                                "long_pct": r.get("long_pct"),
                                "short_pct": r.get("short_pct"),
                                "fund_pct": r.get("fund_pct"),
                                "atr_pct": r.get("atr_pct"),
                                "rsi": r.get("rsi"),
                                "volume": r.get("volume", 0),
                                "change_24h": r.get("change_24h"),
                                "ds_conf": r.get("ds_conf", 0),
                                "persist": r.get("persist", 0),
                                "pump": r.get("pump", False),
                                "pump_ratio": r.get("pump_ratio", 0),
                            })

                    display_rows.sort(key=lambda r: r.get("ds_conf", 0) or 0, reverse=True)
                    active_coins = {r["coin"] for r in rows if r["direction"] in ("LONG", "SHORT") or (r["direction"] == "NONE" and r.get("ds_conf", 0) >= 75)}
                    for coin in list(locked):
                        if coin not in active_coins:
                            del locked[coin]
                    for coin in list(signal_history):
                        if coin not in active_coins:
                            del signal_history[coin]

                    for r in display_rows:
                        pos = trader._open_positions.get(r["coin"])
                        if pos:
                            r["entry"] = pos["entry"]
                            r["target"] = pos["target"]
                            r["sl"] = pos["sl"]
                            r["entry_dir"] = "LONG" if pos["direction"] == "LONG" else "SHORT"
                            r["rr"] = abs((pos["target"] - pos["entry"]) / (pos["entry"] - pos["sl"] + 1e-10)) if pos["direction"] == "LONG" else abs((pos["entry"] - pos["target"]) / (pos["sl"] - pos["entry"] + 1e-10))

                    display.detect_and_notify(display_rows)
                    new_trades = trader.check_and_trade(display_rows)
                    dashboard.update_data(display_rows, btc_trend, candle_str)

                    scanned = len(rows)
                    table = Table(
                        title=f"[bold cyan]1H->15M Scanner | BTC: {btc_trend.upper()} | Next: {candle_str} | {len(display_rows)} signals[/bold cyan]",
                        box=box.SIMPLE,
                        header_style="bold magenta",
                        expand=True,
                    )

                    table.add_column("Coin", style="cyan", no_wrap=True, width=6)
                    table.add_column("Price", justify="right", width=10)
                    table.add_column("Dir", justify="center", width=5)
                    table.add_column("Entry", justify="right", width=10)
                    table.add_column("TP", justify="right", width=10)
                    table.add_column("SL", justify="right", width=10)
                    table.add_column("R:R", justify="center", width=5)
                    table.add_column("Lv", justify="center", width=3)
                    table.add_column("F%", justify="right", width=4)
                    table.add_column("DS%", justify="center", width=5)
                    table.add_column("Pump", justify="center", width=5)
                    table.add_column("Per", justify="center", width=4)

                    for r in display_rows:
                        dir_style = "green" if r["direction"] == "LONG" else "red"
                        dir_text = r["direction"] or "-"

                        lev_style = "green" if str(r.get("leverage", "")).startswith("5") else "yellow" if str(r.get("leverage", "")).startswith("3") else "red"
                        p_text = _fmt(r["price"])
                        entry_text = _fmt(r["entry"]) if r["entry"] else "-"
                        tp_text = _fmt(r["target"]) if r["target"] else "-"
                        sl_text = _fmt(r["sl"]) if r["sl"] else "-"
                        rr_text = f"{r['rr']:.2f}" if r.get("rr", 0) > 0 else "-"

                        fp = r.get("fund_pct", 0)
                        fp_s = f"{fp}%" if fp else "-"
                        if fp >= 75: fp_s = f"[green]{fp}%[/green]"
                        elif fp >= 50: fp_s = f"[yellow]{fp}%[/yellow]"
                        elif fp > 0: fp_s = f"[red]{fp}%[/red]"

                        ds = r.get("ds_conf", 0)
                        ds_s = f"{ds:.0f}%" if ds else "-"
                        if ds >= 80: ds_s = f"[green]{ds:.0f}%[/green]"
                        elif ds >= 60: ds_s = f"[yellow]{ds:.0f}%[/yellow]"
                        else: ds_s = f"[red]{ds:.0f}%[/red]"

                        pump = r.get("pump", False)
                        pump_r = r.get("pump_ratio", 0)
                        pump_s = f"{pump_r}x" if pump else "-"

                        persist = r.get("persist", 0)
                        persist_s = f"{persist}x" if persist > 0 else "-"
                        if persist >= 10: persist_s = f"[green]{persist}x[/green]"
                        elif persist >= 5: persist_s = f"[yellow]{persist}x[/yellow]"
                        elif persist >= 2: persist_s = f"[cyan]{persist}x[/cyan]"

                        table.add_row(
                            r["coin"], p_text,
                            f"[{dir_style}]{dir_text}[/{dir_style}]",
                            entry_text, tp_text, sl_text, rr_text,
                            f"[{lev_style}]{r['leverage']}[/{lev_style}]",
                            str(fp_s), ds_s, pump_s, persist_s,
                        )

                    display.console.clear()
                    display.console.print(table)

                    display.console.print(
                        f"  Passed 1H trend + 15M momentum: {len(display_rows)} signals  |  Updates every 15m on candle close"
                    )

                exited = trader.check_exits(live_prices)
                for e in exited:
                    if "SL" in e.get("reason", ""):
                        _sl_cooldown[e["coin"]] = time.time()
                trader.save_positions()
                dashboard._data["stats"]["next_candle"] = candle_str
                dashboard._data["stats"]["mode"] = "PAPER" if trader.is_paper_mode() else "LIVE" if trader.is_trading_enabled() else "OFF"
                dashboard._data["timestamp"] = datetime.now().strftime("%H:%M:%S")
                dashboard._data["trade_log"] = trader.get_trade_log()
                dashboard._data["open_positions"] = trader.get_positions_with_pnl(live_prices)
                dashboard._data["completed_orders"] = trader.get_completed_orders()
                for r in dashboard._data.get("rows", []):
                    pos = trader._open_positions.get(r["coin"])
                    if pos:
                        r["entry"] = pos["entry"]
                        r["target"] = pos["target"]
                        r["sl"] = pos["sl"]
                        r["entry_dir"] = "LONG" if pos["direction"] == "LONG" else "SHORT"
                        r["rr"] = abs((pos["target"] - pos["entry"]) / (pos["entry"] - pos["sl"] + 1e-10)) if pos["direction"] == "LONG" else abs((pos["entry"] - pos["target"]) / (pos["sl"] - pos["entry"] + 1e-10))
                time.sleep(1)

            except KeyboardInterrupt:
                console.print("\n[yellow]Shutting down...[/yellow]")
                trader._save_positions_now()
                break
            except Exception as e:
                console.print(f"[red]Error in main loop: {e}[/red]")
                traceback.print_exc()
                time.sleep(5)

    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
