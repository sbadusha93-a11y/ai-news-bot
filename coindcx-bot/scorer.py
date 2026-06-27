import numpy as np

_FUND_TOTAL = 5


def _add_fundamental_checks(checks, fund_score, fund_checks):
    ok = 0
    for k, v in fund_checks.items():
        checks[k] = v
        if v:
            ok += 1
    return ok


def _pump_detect(price, high_10, low_10, vol_latest, vol_sma, rsi_val, direction):
    if vol_latest is None or vol_sma is None or vol_sma <= 0:
        return False, 0
    vol_ratio = vol_latest / vol_sma
    if vol_ratio >= 2 and rsi_val > 60 and direction == "LONG":
        return True, round(vol_ratio, 1)
    if vol_ratio >= 2 and rsi_val < 40 and direction == "SHORT":
        return True, round(vol_ratio, 1)
    return False, round(vol_ratio, 1)


def _check_long_setup(price, vwap, ema20, ema50, ema200, rsi_val,
                      macd_line, sig_line, stoch_k, stoch_d, stoch_k_prev, stoch_d_prev,
                      patterns, btc_bullish, fund_score=0, fund_checks=None,
                      vol_latest=None, vol_sma=None, high_10=None, low_10=None):
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

    checks["VolUp"] = vol_latest is not None and vol_sma is not None and vol_sma > 0 and vol_latest > vol_sma
    if checks["VolUp"]: ok += 1

    pump_flag, pump_ratio = _pump_detect(price, high_10, low_10, vol_latest, vol_sma, rsi_val, "LONG")
    checks["Pump"] = pump_flag
    if checks["Pump"]: ok += 1

    ok += _add_fundamental_checks(checks, fund_score, fund_checks or {})
    total = 10 + _FUND_TOTAL
    pct = round(ok / total * 100, 1)
    tech_checks = [checks["P>VWAP"], checks["EMA Ord"], checks["Pull"], checks["Candle"], checks["RSI>50"], checks["MACD B"], checks["StochU"], checks["BTC"], checks["VolUp"], checks["Pump"]]
    core = sum(tech_checks) >= 7
    return core, checks, pct, pump_flag, pump_ratio


def _check_short_setup(price, vwap, ema20, ema50, ema200, rsi_val,
                       macd_line, sig_line, stoch_k, stoch_d, stoch_k_prev, stoch_d_prev,
                       patterns, btc_bearish, fund_score=0, fund_checks=None,
                       vol_latest=None, vol_sma=None, high_10=None, low_10=None):
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

    checks["VolUp"] = vol_latest is not None and vol_sma is not None and vol_sma > 0 and vol_latest > vol_sma
    if checks["VolUp"]: ok += 1

    pump_flag, pump_ratio = _pump_detect(price, high_10, low_10, vol_latest, vol_sma, rsi_val, "SHORT")
    checks["Pump"] = pump_flag
    if checks["Pump"]: ok += 1

    ok += _add_fundamental_checks(checks, fund_score, fund_checks or {})
    total = 10 + _FUND_TOTAL
    pct = round(ok / total * 100, 1)
    tech_checks = [checks["P<VWAP"], checks["EMA Ord"], checks["Pull"], checks["Candle"], checks["RSI<50"], checks["MACD B"], checks["StochD"], checks["BTC"], checks["VolUp"], checks["Pump"]]
    core = sum(tech_checks) >= 7
    return core, checks, pct, pump_flag, pump_ratio


def get_signal(price, vwap, ema20, ema50, ema200, rsi_val,
               macd_line, sig_line, macd_hist,
               stoch_k, stoch_d, stoch_k_prev, stoch_d_prev,
               patterns, btc_trend, fund_score=0, fund_checks=None,
               vol_latest=None, vol_sma=None, high_10=None, low_10=None):
    btc_bull = btc_trend in ("bullish", "neutral")
    btc_bear = btc_trend in ("bearish", "neutral")

    fund_checks = fund_checks or {}
    long_core, long_checks, long_pct, long_pump, long_pump_r = _check_long_setup(
        price, vwap, ema20, ema50, ema200, rsi_val,
        macd_line, sig_line, stoch_k, stoch_d, stoch_k_prev, stoch_d_prev,
        patterns, btc_bull, fund_score, fund_checks,
        vol_latest, vol_sma, high_10, low_10,
    )
    short_core, short_checks, short_pct, short_pump, short_pump_r = _check_short_setup(
        price, vwap, ema20, ema50, ema200, rsi_val,
        macd_line, sig_line, stoch_k, stoch_d, stoch_k_prev, stoch_d_prev,
        patterns, btc_bear, fund_score, fund_checks,
        vol_latest, vol_sma, high_10, low_10,
    )

    pump_flag = long_pump or short_pump
    pump_ratio = long_pump_r if long_pump else short_pump_r

    if long_core and long_pct >= short_pct:
        return "LONG", "LONG", long_checks, long_pct, short_pct, pump_flag, pump_ratio
    if short_core and short_pct >= long_pct:
        return "SHORT", "SHORT", short_checks, long_pct, short_pct, pump_flag, pump_ratio
    return "HOLD", "NONE", None, long_pct, short_pct, pump_flag, pump_ratio


def calculate_target_sl(entry, atr_val, high_10, low_10, ema20, direction):
    if atr_val is None or (isinstance(atr_val, float) and np.isnan(atr_val)) or atr_val == 0:
        atr_val = entry * 0.02
    sl_distance = max(atr_val * 1.5, entry * 0.008)
    if direction == "LONG":
        sl = low_10 - sl_distance
        target = entry + (entry - sl) * 3.0
    else:
        sl = high_10 + sl_distance
        target = entry - (sl - entry) * 3.0
    rr = abs((target - entry) / (entry - sl + 1e-10)) if direction == "LONG" else abs((entry - target) / (sl - entry + 1e-10))
    return round(target, 8), round(sl, 8), round(rr, 2)


def calculate_entry(high, low, close, high_10, low_10, direction):
    return round(close, 8)


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
