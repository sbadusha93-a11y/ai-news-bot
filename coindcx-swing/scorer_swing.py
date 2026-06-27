import numpy as np


def _check_long_setup(price, vwap, ema20, ema50, ema200, rsi_val,
                      macd_line, sig_line, stoch_k, stoch_d, stoch_k_prev, stoch_d_prev,
                      patterns, btc_bullish):
    checks = {}
    ok = 0

    checks["P>VWAP"] = price > vwap
    checks["EMA Ord"] = ema20 > ema50 > ema200
    if checks["P>VWAP"]: ok += 1
    if checks["EMA Ord"]: ok += 1

    d_ema = abs(price - ema20) / ema20 * 100
    d_vwap = abs(price - vwap) / vwap * 100
    checks["Pull"] = d_ema < 3 or d_vwap < 3
    if checks["Pull"]: ok += 1

    checks["Candle"] = patterns.get("bullish_engulfing", False) or patterns.get("hammer", False) or patterns.get("strong_bull", False)
    checks["B_Eng"] = patterns.get("bullish_engulfing", False)
    checks["Hamm"] = patterns.get("hammer", False)
    checks["StrB"] = patterns.get("strong_bull", False)
    if checks["Candle"]: ok += 1

    checks["RSI>50"] = rsi_val > 50
    checks["MACD B"] = macd_line > sig_line
    checks["StochU"] = stoch_k_prev < stoch_d_prev and stoch_k > stoch_d
    if checks["RSI>50"]: ok += 1
    if checks["MACD B"]: ok += 1
    if checks["StochU"]: ok += 1

    checks["BTC"] = btc_bullish
    if checks["BTC"]: ok += 1

    pct = round(ok / 8 * 100, 1)
    core = checks["P>VWAP"] and checks["EMA Ord"] and checks["Candle"] and checks["RSI>50"] and checks["MACD B"]
    return core, checks, pct


def _check_short_setup(price, vwap, ema20, ema50, ema200, rsi_val,
                       macd_line, sig_line, stoch_k, stoch_d, stoch_k_prev, stoch_d_prev,
                       patterns, btc_bearish):
    checks = {}
    ok = 0

    checks["P<VWAP"] = price < vwap
    checks["EMA Ord"] = ema20 < ema50 < ema200
    if checks["P<VWAP"]: ok += 1
    if checks["EMA Ord"]: ok += 1

    d_ema = abs(price - ema20) / ema20 * 100
    d_vwap = abs(price - vwap) / vwap * 100
    checks["Pull"] = d_ema < 3 or d_vwap < 3
    if checks["Pull"]: ok += 1

    checks["Candle"] = patterns.get("bearish_engulfing", False) or patterns.get("shooting_star", False) or patterns.get("strong_bear", False)
    checks["B_Eng"] = patterns.get("bearish_engulfing", False)
    checks["SS"] = patterns.get("shooting_star", False)
    checks["StrB"] = patterns.get("strong_bear", False)
    if checks["Candle"]: ok += 1

    checks["RSI<50"] = rsi_val < 50
    checks["MACD B"] = macd_line < sig_line
    checks["StochD"] = stoch_k_prev > stoch_d_prev and stoch_k < stoch_d
    if checks["RSI<50"]: ok += 1
    if checks["MACD B"]: ok += 1
    if checks["StochD"]: ok += 1

    checks["BTC"] = btc_bearish
    if checks["BTC"]: ok += 1

    pct = round(ok / 8 * 100, 1)
    core = checks["P<VWAP"] and checks["EMA Ord"] and checks["Candle"] and checks["RSI<50"] and checks["MACD B"]
    return core, checks, pct


def get_signal(price, vwap, ema20, ema50, ema200, rsi_val,
               macd_line, sig_line, macd_hist,
               stoch_k, stoch_d, stoch_k_prev, stoch_d_prev,
               patterns, btc_trend):
    btc_bull = btc_trend in ("bullish", "neutral")
    btc_bear = btc_trend in ("bearish", "neutral")

    long_core, long_checks, long_pct = _check_long_setup(
        price, vwap, ema20, ema50, ema200, rsi_val,
        macd_line, sig_line, stoch_k, stoch_d, stoch_k_prev, stoch_d_prev,
        patterns, btc_bull
    )
    short_core, short_checks, short_pct = _check_short_setup(
        price, vwap, ema20, ema50, ema200, rsi_val,
        macd_line, sig_line, stoch_k, stoch_d, stoch_k_prev, stoch_d_prev,
        patterns, btc_bear
    )

    if long_core and long_pct >= short_pct:
        return "BUY LONG", "LONG", long_checks, long_pct, short_pct
    if short_core and short_pct >= long_pct:
        return "SELL SHORT", "SHORT", short_checks, long_pct, short_pct
    return "HOLD", "NONE", None, long_pct, short_pct


def calculate_target_sl(entry, atr_val, high_10, low_10, direction):
    if np.isnan(atr_val) or atr_val == 0:
        atr_val = entry * 0.02
    sl_distance = max(atr_val * 1.0, entry * 0.005)
    if direction == "LONG":
        sl = low_10 - sl_distance
        target = entry + (entry - sl) * 2.0
        tp1 = entry + (entry - sl) * 1.0
        tp2 = entry + (entry - sl) * 3.0
    else:
        sl = high_10 + sl_distance
        target = entry - (sl - entry) * 2.0
        tp1 = entry - (sl - entry) * 1.0
        tp2 = entry - (sl - entry) * 3.0
    rr = abs((target - entry) / (entry - sl + 1e-10)) if direction == "LONG" else abs((entry - target) / (sl - entry + 1e-10))
    return round(target, 8), round(sl, 8), round(rr, 2), round(tp1, 8), round(tp2, 8)


def calculate_entry(high, low, close, high_10, low_10, direction):
    if direction == "NONE":
        return close
    pivot = (high + low + close) / 3
    support = 2 * pivot - high
    resistance = 2 * pivot - low
    if direction == "LONG":
        entry = min(support, close)
        entry = max(entry, low_10)
    else:
        entry = max(resistance, close)
        entry = min(entry, high_10)
    return round(entry, 8)


def check_long_exit(close, ema20, rsi_val, macd_line, sig_line, entry, target, sl):
    reasons = []
    if rsi_val < 50:
        reasons.append("RSI<50")
    if macd_line < sig_line:
        reasons.append("MACD Bear Cross")
    if close < ema20:
        reasons.append("Close<EMA20")
    if target and close >= target:
        reasons.append("TP HIT")
    if sl and close <= sl:
        reasons.append("SL HIT")
    return reasons


def check_short_exit(close, ema20, rsi_val, macd_line, sig_line, entry, target, sl):
    reasons = []
    if rsi_val > 50:
        reasons.append("RSI>50")
    if macd_line > sig_line:
        reasons.append("MACD Bull Cross")
    if close > ema20:
        reasons.append("Close>EMA20")
    if target and close <= target:
        reasons.append("TP HIT")
    if sl and close >= sl:
        reasons.append("SL HIT")
    return reasons


def check_volatility(atr_val, atr_sma_20):
    if atr_val is None or atr_sma_20 is None or np.isnan(atr_val) or np.isnan(atr_sma_20):
        return True
    return atr_val > atr_sma_20 * 0.8
