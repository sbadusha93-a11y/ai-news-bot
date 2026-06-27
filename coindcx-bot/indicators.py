import numpy as np
import pandas as pd


def ema(data, period):
    return pd.Series(data).ewm(span=period, adjust=False).mean().values


def rsi(close, period=14):
    close = pd.Series(close, dtype=float)
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_vals = 100 - (100 / (1 + rs))
    rsi_vals = rsi_vals.fillna(50).values
    return rsi_vals


def macd(data, fast=12, slow=26, signal=9):
    e_fast = ema(data, fast)
    e_slow = ema(data, slow)
    macd_line = e_fast - e_slow
    sig_line = ema(macd_line, signal)
    hist = macd_line - sig_line
    return macd_line, sig_line, hist


def stochastic(high, low, close, k_period=14, d_period=3):
    h = pd.Series(high, dtype=float)
    l = pd.Series(low, dtype=float)
    c = pd.Series(close, dtype=float)
    low_min = l.rolling(k_period).min()
    high_max = h.rolling(k_period).max()
    k = 100 * (c - low_min) / (high_max - low_min).replace(0, np.nan)
    d = k.rolling(d_period).mean()
    return k.fillna(50).values, d.fillna(50).values


def volume_sma(volume, period=20):
    return pd.Series(volume, dtype=float).rolling(period).mean().values


def atr(high, low, close, period=14):
    h = pd.Series(high, dtype=float)
    l = pd.Series(low, dtype=float)
    c = pd.Series(close, dtype=float)
    tr = pd.concat([
        h - l,
        (h - c.shift()).abs(),
        (l - c.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean().fillna(tr.ewm(span=period, adjust=False).mean()).values


def highest(data, period):
    return pd.Series(data, dtype=float).rolling(period).max().values


def lowest(data, period):
    return pd.Series(data, dtype=float).rolling(period).min().values


def vwap(high, low, close, volume, period=20):
    typical_price = (high + low + close) / 3
    v = pd.Series(volume, dtype=float)
    tp = pd.Series(typical_price, dtype=float)
    cum_vp = (tp * v).rolling(window=period, min_periods=1).sum()
    cum_v = v.rolling(window=period, min_periods=1).sum()
    return (cum_vp / cum_v.replace(0, np.nan)).ffill().values


def stoch_rsi(close, period=14, k_period=3, d_period=3):
    rsi_vals = rsi(close, period)
    rsi_series = pd.Series(rsi_vals, dtype=float)
    min_rsi = rsi_series.rolling(period).min()
    max_rsi = rsi_series.rolling(period).max()
    stoch_k = 100 * (rsi_series - min_rsi) / (max_rsi - min_rsi).replace(0, np.nan)
    k = stoch_k.rolling(k_period).mean()
    d = k.rolling(d_period).mean()
    return k.fillna(50).values, d.fillna(50).values


def adx(high, low, close, period=14):
    h = pd.Series(high, dtype=float)
    l = pd.Series(low, dtype=float)
    c = pd.Series(close, dtype=float)

    tr = pd.concat([
        h - l,
        (h - c.shift()).abs(),
        (l - c.shift()).abs()
    ], axis=1).max(axis=1)

    up_move = h - h.shift(1)
    down_move = l.shift(1) - l

    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), dtype=float)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), dtype=float)

    atr_val = tr.ewm(span=period, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(span=period, adjust=False).mean() / atr_val.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(span=period, adjust=False).mean() / atr_val.replace(0, np.nan)

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx_val = dx.ewm(span=period, adjust=False).mean()

    return adx_val.fillna(25).values, plus_di.fillna(25).values, minus_di.fillna(25).values


def detect_candle_pattern(open, high, low, close, prev_open, prev_high, prev_low, prev_close):
    body = abs(close - open)
    prev_body = abs(prev_close - prev_open)
    upper_wick = high - max(open, close)
    lower_wick = min(open, close) - low
    patterns = {}

    if body > 0 and prev_body > 0:
        if prev_close < prev_open and close > open:
            if close > prev_open and open < prev_close:
                patterns["bullish_engulfing"] = True
        if prev_close > prev_open and close < open:
            if open > prev_close and close < prev_open:
                patterns["bearish_engulfing"] = True

    if body > 0 and lower_wick >= 2 * body and upper_wick <= 0.3 * body:
        patterns["hammer"] = True

    if body > 0 and upper_wick >= 2 * body and lower_wick <= 0.3 * body:
        patterns["shooting_star"] = True

    if close > open and body > prev_body * 1.5:
        patterns["strong_bull"] = True

    if close < open and body > prev_body * 1.5:
        patterns["strong_bear"] = True

    return patterns
