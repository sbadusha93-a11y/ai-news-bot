import numpy as np
import pandas as pd
from loguru import logger

from src.config import bot_config


class TechnicalIndicators:
    def __init__(self):
        self.indicator_settings = bot_config["indicator_settings"]

    def compute_all(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 30:
            return df

        df = df.copy()
        df = self._rsi(df)
        df = self._stoch_rsi(df)
        df = self._macd(df)
        df = self._ema(df)
        df = self._bollinger_bands(df)
        df = self._atr(df)
        df = self._adx(df)
        df = self._cci(df)
        df = self._roc(df)
        df = self._momentum(df)
        df = self._supertrend(df)
        df = self._ichimoku(df)
        df = self._parabolic_sar(df)
        df = self._donchian_channel(df)
        df = self._keltner_channel(df)
        df = self._vwap(df)
        df = self._pivot_points(df)
        df = self._fibonacci_levels(df)

        return df

    def _rsi(self, df: pd.DataFrame, period: int = None) -> pd.DataFrame:
        if period is None:
            period = self.indicator_settings["rsi_period"]
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.nan)
        df["rsi"] = 100 - (100 / (1 + rs))
        df["rsi_signal"] = np.where(
            df["rsi"] < 30, "oversold",
            np.where(df["rsi"] > 70, "overbought", "neutral")
        )
        return df

    def _stoch_rsi(self, df: pd.DataFrame, period: int = None) -> pd.DataFrame:
        if period is None:
            period = self.indicator_settings["stoch_rsi_period"]
        rsi = df.get("rsi", self._rsi(df.copy())["rsi"])
        min_rsi = rsi.rolling(window=period).min()
        max_rsi = rsi.rolling(window=period).max()
        df["stoch_rsi"] = ((rsi - min_rsi) / (max_rsi - min_rsi).replace(0, np.nan)) * 100
        df["stoch_rsi_k"] = df["stoch_rsi"].rolling(window=3).mean()
        df["stoch_rsi_d"] = df["stoch_rsi_k"].rolling(window=3).mean()
        df["stoch_rsi_signal"] = np.where(
            df["stoch_rsi"] < 20, "oversold",
            np.where(df["stoch_rsi"] > 80, "overbought", "neutral")
        )
        return df

    def _macd(self, df: pd.DataFrame) -> pd.DataFrame:
        s = self.indicator_settings
        fast = s["macd_fast"]
        slow = s["macd_slow"]
        signal = s["macd_signal"]
        ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
        ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
        df["macd"] = ema_fast - ema_slow
        df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
        df["macd_histogram"] = df["macd"] - df["macd_signal"]
        df["macd_signal_line"] = np.where(
            df["macd"] > df["macd_signal"], "bullish",
            np.where(df["macd"] < df["macd_signal"], "bearish", "neutral")
        )
        df["macd_histogram_signal"] = np.where(
            df["macd_histogram"] > df["macd_histogram"].shift(1), "increasing",
            "decreasing"
        )
        return df

    def _ema(self, df: pd.DataFrame) -> pd.DataFrame:
        periods = self.indicator_settings["ema_periods"]
        for period in periods:
            df[f"ema_{period}"] = df["close"].ewm(span=period, adjust=False).mean()

        for p1, p2 in [(9, 20), (20, 50), (50, 100), (100, 200)]:
            if f"ema_{p1}" in df.columns and f"ema_{p2}" in df.columns:
                df[f"ema_{p1}_{p2}_cross"] = np.where(
                    df[f"ema_{p1}"] > df[f"ema_{p2}"], "bullish", "bearish"
                )
        return df

    def _bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        period = self.indicator_settings["bollinger_period"]
        std_dev = self.indicator_settings["bollinger_std"]
        df["bb_middle"] = df["close"].rolling(window=period).mean()
        bb_std = df["close"].rolling(window=period).std()
        df["bb_upper"] = df["bb_middle"] + (bb_std * std_dev)
        df["bb_lower"] = df["bb_middle"] - (bb_std * std_dev)
        df["bb_width"] = df["bb_upper"] - df["bb_lower"]
        df["bb_position"] = (
            (df["close"] - df["bb_lower"]) / (df["bb_width"]).replace(0, np.nan)
        )
        df["bb_signal"] = np.where(
            df["close"] > df["bb_upper"], "overbought",
            np.where(df["close"] < df["bb_lower"], "oversold", "neutral")
        )
        return df

    def _atr(self, df: pd.DataFrame, period: int = None) -> pd.DataFrame:
        if period is None:
            period = self.indicator_settings["atr_period"]
        high_low = df["high"] - df["low"]
        high_close = (df["high"] - df["close"].shift()).abs()
        low_close = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df["atr"] = tr.rolling(window=period).mean()
        df["atr_percent"] = (df["atr"] / df["close"]) * 100
        return df

    def _adx(self, df: pd.DataFrame, period: int = None) -> pd.DataFrame:
        if period is None:
            period = self.indicator_settings["adx_period"]
        df["tr"] = pd.concat([
            df["high"] - df["low"],
            (df["high"] - df["close"].shift()).abs(),
            (df["low"] - df["close"].shift()).abs(),
        ], axis=1).max(axis=1)

        df["up_move"] = df["high"] - df["high"].shift()
        df["down_move"] = df["low"].shift() - df["low"]
        df["+dm"] = np.where(
            (df["up_move"] > df["down_move"]) & (df["up_move"] > 0),
            df["up_move"], 0
        )
        df["-dm"] = np.where(
            (df["down_move"] > df["up_move"]) & (df["down_move"] > 0),
            df["down_move"], 0
        )

        df["+di"] = 100 * (
            df["+dm"].ewm(span=period).mean() / df["tr"].ewm(span=period).mean()
        )
        df["-di"] = 100 * (
            df["-dm"].ewm(span=period).mean() / df["tr"].ewm(span=period).mean()
        )
        df["dx"] = 100 * (
            (df["+di"] - df["-di"]).abs()
            / (df["+di"] + df["-di"]).replace(0, np.nan)
        )
        df["adx"] = df["dx"].ewm(span=period).mean()
        df["adx_signal"] = np.where(
            df["adx"] >= 25, "strong_trend",
            np.where(df["adx"] >= 20, "moderate_trend", "weak_trend")
        )
        df["di_signal"] = np.where(
            df["+di"] > df["-di"], "bullish", "bearish"
        )
        return df

    def _cci(self, df: pd.DataFrame, period: int = None) -> pd.DataFrame:
        if period is None:
            period = self.indicator_settings["cci_period"]
        tp = (df["high"] + df["low"] + df["close"]) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(
            lambda x: np.abs(x - x.mean()).mean()
        )
        df["cci"] = (tp - sma) / (0.015 * mad.replace(0, np.nan))
        df["cci_signal"] = np.where(
            df["cci"] > 100, "overbought",
            np.where(df["cci"] < -100, "oversold", "neutral")
        )
        return df

    def _roc(self, df: pd.DataFrame, period: int = None) -> pd.DataFrame:
        if period is None:
            period = self.indicator_settings["roc_period"]
        df["roc"] = ((df["close"] - df["close"].shift(period)) / df["close"].shift(period)) * 100
        df["roc_signal"] = np.where(
            df["roc"] > 0, "positive_momentum", "negative_momentum"
        )
        return df

    def _momentum(self, df: pd.DataFrame, period: int = None) -> pd.DataFrame:
        if period is None:
            period = self.indicator_settings["momentum_period"]
        df["momentum"] = df["close"] - df["close"].shift(period)
        df["momentum_signal"] = np.where(
            df["momentum"] > 0, "positive", "negative"
        )
        return df

    def _supertrend(self, df: pd.DataFrame) -> pd.DataFrame:
        period = self.indicator_settings["supertrend_period"]
        multiplier = self.indicator_settings["supertrend_multiplier"]

        if "atr" not in df.columns:
            df = self._atr(df)

        hl_avg = (df["high"] + df["low"]) / 2
        df["st_upper"] = hl_avg + (multiplier * df["atr"])
        df["st_lower"] = hl_avg - (multiplier * df["atr"])

        df["st_trend"] = 1
        df["st_support"] = 0.0
        df["st_resistance"] = 0.0

        for i in range(1, len(df)):
            prev_trend = df["st_trend"].iloc[i - 1]
            if prev_trend == 1:
                if df["close"].iloc[i] <= df["st_lower"].iloc[i - 1]:
                    df.loc[df.index[i], "st_trend"] = -1
                else:
                    df.loc[df.index[i], "st_trend"] = 1
            else:
                if df["close"].iloc[i] >= df["st_upper"].iloc[i - 1]:
                    df.loc[df.index[i], "st_trend"] = 1
                else:
                    df.loc[df.index[i], "st_trend"] = -1

            if df["st_trend"].iloc[i] == 1:
                df.loc[df.index[i], "st_support"] = df["st_lower"].iloc[i]
                df.loc[df.index[i], "st_resistance"] = df["st_upper"].iloc[i]

        df["st_direction"] = np.where(df["st_trend"] == 1, "uptrend", "downtrend")
        return df

    def _ichimoku(self, df: pd.DataFrame) -> pd.DataFrame:
        conv = self.indicator_settings["ichimoku_conversion"]
        base = self.indicator_settings["ichimoku_base"]
        span = self.indicator_settings["ichimoku_span"]

        df["ichimoku_conversion"] = (
            df["high"].rolling(window=conv).max()
            + df["low"].rolling(window=conv).min()
        ) / 2
        df["ichimoku_base"] = (
            df["high"].rolling(window=base).max()
            + df["low"].rolling(window=base).min()
        ) / 2
        df["ichimoku_span_a"] = (
            (df["ichimoku_conversion"] + df["ichimoku_base"]) / 2
        ).shift(base)
        df["ichimoku_span_b"] = (
            (
                df["high"].rolling(window=span).max()
                + df["low"].rolling(window=span).min()
            ) / 2
        ).shift(base)
        df["ichimoku_lagging"] = df["close"].shift(-base)

        df["ichimoku_cloud"] = np.where(
            df["ichimoku_span_a"] > df["ichimoku_span_b"], "bullish", "bearish"
        )
        df["ichimoku_signal"] = np.where(
            df["close"] > df["ichimoku_span_a"], "bullish",
            np.where(df["close"] < df["ichimoku_span_a"], "bearish", "neutral")
        )
        df["ichimoku_tk_cross"] = np.where(
            df["ichimoku_conversion"] > df["ichimoku_base"], "bullish_cross",
            np.where(df["ichimoku_conversion"] < df["ichimoku_base"], "bearish_cross", "neutral")
        )
        return df

    def _parabolic_sar(self, df: pd.DataFrame) -> pd.DataFrame:
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        length = len(df)

        psar = np.zeros(length)
        trend = np.zeros(length)
        af = np.zeros(length)
        ep = np.zeros(length)

        if length < 2:
            return df

        trend[0] = 1
        af[0] = 0.02
        ep[0] = high[0]
        psar[0] = low[0]

        for i in range(1, length):
            if trend[i - 1] == 1:
                psar[i] = psar[i - 1] + af[i - 1] * (ep[i - 1] - psar[i - 1])
                psar[i] = min(psar[i], low[i - 1], low[i])
                if high[i] > ep[i - 1]:
                    ep[i] = high[i]
                    af[i] = min(af[i - 1] + 0.02, 0.2)
                else:
                    ep[i] = ep[i - 1]
                    af[i] = af[i - 1]
                if low[i] < psar[i]:
                    trend[i] = -1
                    psar[i] = ep[i - 1]
                    ep[i] = low[i]
                    af[i] = 0.02
                else:
                    trend[i] = 1
            else:
                psar[i] = psar[i - 1] + af[i - 1] * (ep[i - 1] - psar[i - 1])
                psar[i] = max(psar[i], high[i - 1], high[i])
                if low[i] < ep[i - 1]:
                    ep[i] = low[i]
                    af[i] = min(af[i - 1] + 0.02, 0.2)
                else:
                    ep[i] = ep[i - 1]
                    af[i] = af[i - 1]
                if high[i] > psar[i]:
                    trend[i] = 1
                    psar[i] = ep[i - 1]
                    ep[i] = high[i]
                    af[i] = 0.02
                else:
                    trend[i] = -1

        df["psar"] = psar
        df["psar_trend"] = np.where(trend == 1, "uptrend", "downtrend")
        df["psar_signal"] = np.where(
            (trend == 1) & (np.roll(trend, 1) == -1), "reversal_up",
            np.where((trend == -1) & (np.roll(trend, 1) == 1), "reversal_down", "neutral")
        )
        return df

    def _donchian_channel(self, df: pd.DataFrame) -> pd.DataFrame:
        period = self.indicator_settings["donchian_period"]
        df["donchian_upper"] = df["high"].rolling(window=period).max()
        df["donchian_lower"] = df["low"].rolling(window=period).min()
        df["donchian_middle"] = (df["donchian_upper"] + df["donchian_lower"]) / 2
        df["donchian_width"] = df["donchian_upper"] - df["donchian_lower"]
        df["donchian_signal"] = np.where(
            df["close"] > df["donchian_upper"].shift(1), "breakout_up",
            np.where(df["close"] < df["donchian_lower"].shift(1), "breakout_down", "neutral")
        )
        return df

    def _keltner_channel(self, df: pd.DataFrame) -> pd.DataFrame:
        period = self.indicator_settings["keltner_period"]
        multiplier = self.indicator_settings["keltner_atr_multiplier"]
        if "atr" not in df.columns:
            df = self._atr(df)
        df["kc_middle"] = df["close"].ewm(span=period).mean()
        df["kc_upper"] = df["kc_middle"] + (multiplier * df["atr"])
        df["kc_lower"] = df["kc_middle"] - (multiplier * df["atr"])
        df["kc_width"] = df["kc_upper"] - df["kc_lower"]
        df["kc_signal"] = np.where(
            df["close"] > df["kc_upper"], "overbought",
            np.where(df["close"] < df["kc_lower"], "oversold", "neutral")
        )
        return df

    def _vwap(self, df: pd.DataFrame, period: int = None) -> pd.DataFrame:
        if period is None:
            period = self.indicator_settings["vwap_period"]
        tp = (df["high"] + df["low"] + df["close"]) / 3
        df["vwap"] = (
            (tp * df["volume"]).rolling(window=period).sum()
            / df["volume"].rolling(window=period).sum().replace(0, np.nan)
        )
        df["vwap_signal"] = np.where(
            df["close"] > df["vwap"], "above_vwap", "below_vwap"
        )
        return df

    def _pivot_points(self, df: pd.DataFrame) -> pd.DataFrame:
        df["pivot"] = (df["high"] + df["low"] + df["close"]) / 3
        df["r1"] = 2 * df["pivot"] - df["low"]
        df["r2"] = df["pivot"] + (df["high"] - df["low"])
        df["r3"] = df["high"] + 2 * (df["pivot"] - df["low"])
        df["s1"] = 2 * df["pivot"] - df["high"]
        df["s2"] = df["pivot"] - (df["high"] - df["low"])
        df["s3"] = df["low"] - 2 * (df["high"] - df["pivot"])
        return df

    def _fibonacci_levels(self, df: pd.DataFrame, period: int = 100) -> pd.DataFrame:
        high = df["high"].rolling(window=period).max()
        low = df["low"].rolling(window=period).min()
        diff = high - low
        df["fib_238"] = high - diff * 0.236
        df["fib_382"] = high - diff * 0.382
        df["fib_500"] = high - diff * 0.5
        df["fib_618"] = high - diff * 0.618
        df["fib_786"] = high - diff * 0.786
        return df
