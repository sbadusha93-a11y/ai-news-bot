import numpy as np
import pandas as pd
from loguru import logger


class PriceActionIndicators:
    def __init__(self):
        pass

    def compute_all(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 20:
            return df

        df = df.copy()
        df = self._candlestick_patterns(df)
        df = self._supply_demand(df)
        df = self._support_resistance(df)
        df = self._trendlines(df)
        df = self._chart_patterns(df)

        return df

    def _candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        body = abs(df["close"] - df["open"])
        upper_wick = df["high"] - df[["close", "open"]].max(axis=1)
        lower_wick = df[["close", "open"]].min(axis=1) - df["low"]
        total_range = df["high"] - df["low"]

        df["bullish_engulfing"] = False
        df["bearish_engulfing"] = False
        df["inside_bar"] = False
        df["outside_bar"] = False
        df["hammer"] = False
        df["shooting_star"] = False
        df["morning_star"] = False
        df["evening_star"] = False
        df["doji"] = False

        for i in range(1, len(df)):
            prev_close = df["close"].iloc[i - 1]
            prev_open = df["open"].iloc[i - 1]
            curr_close = df["close"].iloc[i]
            curr_open = df["open"].iloc[i]
            prev_body = abs(prev_close - prev_open)
            curr_body = abs(curr_close - curr_open)
            prev_range = df["high"].iloc[i - 1] - df["low"].iloc[i - 1]
            curr_range = df["high"].iloc[i] - df["low"].iloc[i]

            if curr_close > curr_open and prev_close < prev_open:
                if curr_open < prev_close and curr_close > prev_open:
                    df.loc[df.index[i], "bullish_engulfing"] = True

            if curr_close < curr_open and prev_close > prev_open:
                if curr_open > prev_close and curr_close < prev_open:
                    df.loc[df.index[i], "bearish_engulfing"] = True

            if df["high"].iloc[i] <= df["high"].iloc[i - 1] and \
               df["low"].iloc[i] >= df["low"].iloc[i - 1]:
                df.loc[df.index[i], "inside_bar"] = True

            if df["high"].iloc[i] > df["high"].iloc[i - 1] and \
               df["low"].iloc[i] < df["low"].iloc[i - 1]:
                df.loc[df.index[i], "outside_bar"] = True

            body_ratio = curr_body / curr_range if curr_range > 0 else 0
            uw_ratio = upper_wick.iloc[i] / curr_range if curr_range > 0 else 0
            lw_ratio = lower_wick.iloc[i] / curr_range if curr_range > 0 else 0

            if body_ratio < 0.3 and lw_ratio > 0.6 and uw_ratio < 0.1:
                df.loc[df.index[i], "hammer"] = True

            if body_ratio < 0.3 and uw_ratio > 0.6 and lw_ratio < 0.1:
                df.loc[df.index[i], "shooting_star"] = True

            if body_ratio < 0.1:
                df.loc[df.index[i], "doji"] = True

            if i >= 2:
                b1 = abs(df["close"].iloc[i - 2] - df["open"].iloc[i - 2])
                b2 = abs(df["close"].iloc[i - 1] - df["open"].iloc[i - 1])
                if df["close"].iloc[i - 2] < df["open"].iloc[i - 2] and \
                   b2 / (df["high"].iloc[i - 1] - df["low"].iloc[i - 1]) < 0.1 and \
                   df["close"].iloc[i] > df["open"].iloc[i] and \
                   df["close"].iloc[i] > (df["high"].iloc[i - 2] + df["low"].iloc[i - 2]) / 2:
                    df.loc[df.index[i], "morning_star"] = True

                if df["close"].iloc[i - 2] > df["open"].iloc[i - 2] and \
                   b2 / (df["high"].iloc[i - 1] - df["low"].iloc[i - 1]) < 0.1 and \
                   df["close"].iloc[i] < df["open"].iloc[i] and \
                   df["close"].iloc[i] < (df["high"].iloc[i - 2] + df["low"].iloc[i - 2]) / 2:
                    df.loc[df.index[i], "evening_star"] = True

        df["bullish_pattern"] = df["bullish_engulfing"] | df["hammer"] | \
                                df["morning_star"]
        df["bearish_pattern"] = df["bearish_engulfing"] | df["shooting_star"] | \
                                df["evening_star"]

        return df

    def _supply_demand(self, df: pd.DataFrame) -> pd.DataFrame:
        df["demand_zone"] = 0.0
        df["supply_zone"] = 0.0
        lookback = 20

        for i in range(lookback, len(df)):
            window = df.iloc[i - lookback:i]
            if df["volume"].iloc[i] > window["volume"].mean() * 1.5:
                if df["close"].iloc[i] > df["open"].iloc[i]:
                    zone = df["low"].iloc[i]
                    df.loc[df.index[i], "demand_zone"] = zone
                else:
                    zone = df["high"].iloc[i]
                    df.loc[df.index[i], "supply_zone"] = zone

        return df

    def _support_resistance(self, df: pd.DataFrame) -> pd.DataFrame:
        df["support"] = 0.0
        df["resistance"] = 0.0
        lookback = 50

        for i in range(lookback, len(df)):
            window = df.iloc[i - lookback:i]
            current_price = df["close"].iloc[i]

            swing_highs = window[window["swing_high"]] if "swing_high" in window.columns else pd.DataFrame()
            swing_lows = window[window["swing_low"]] if "swing_low" in window.columns else pd.DataFrame()

            if not swing_highs.empty:
                nearest_resistance = swing_highs[
                    swing_highs["high"] > current_price
                ]["high"].min() if any(swing_highs["high"] > current_price) else 0
                df.loc[df.index[i], "resistance"] = nearest_resistance

            if not swing_lows.empty:
                nearest_support = swing_lows[
                    swing_lows["low"] < current_price
                ]["low"].max() if any(swing_lows["low"] < current_price) else 0
                df.loc[df.index[i], "support"] = nearest_support

        return df

    def _trendlines(self, df: pd.DataFrame) -> pd.DataFrame:
        df["uptrend_line"] = 0.0
        df["downtrend_line"] = 0.0
        lookback = 30

        for i in range(lookback, len(df)):
            window = df.iloc[i - lookback:i]
            lows = window["low"].values
            highs = window["high"].values
            x = np.arange(len(lows))

            if len(lows) > 5:
                low_indices = np.where(
                    (lows[1:-1] < lows[:-2]) & (lows[1:-1] < lows[2:])
                )[0] + 1
                if len(low_indices) >= 2:
                    recent_lows = lows[low_indices[-2:]]
                    slope = (recent_lows[1] - recent_lows[0]) / (low_indices[-1] - low_indices[-2])
                    df.loc[df.index[i], "uptrend_line"] = \
                        recent_lows[1] + slope * (lookback - low_indices[-1])

                high_indices = np.where(
                    (highs[1:-1] > highs[:-2]) & (highs[1:-1] > highs[2:])
                )[0] + 1
                if len(high_indices) >= 2:
                    recent_highs = highs[high_indices[-2:]]
                    slope = (recent_highs[1] - recent_highs[0]) / (high_indices[-1] - high_indices[-2])
                    df.loc[df.index[i], "downtrend_line"] = \
                        recent_highs[1] + slope * (lookback - high_indices[-1])

        return df

    def _chart_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        df["double_top"] = False
        df["double_bottom"] = False
        df["head_shoulders"] = False
        df["inverse_head_shoulders"] = False
        lookback = 40

        for i in range(lookback, len(df)):
            window = df.iloc[i - lookback:i]
            high_points = window[window["swing_high"]] if "swing_high" in window.columns else pd.DataFrame()
            low_points = window[window["swing_low"]] if "swing_low" in window.columns else pd.DataFrame()

            if len(high_points) >= 2:
                last_two = high_points.iloc[-2:]
                high_diff = abs(last_two["high"].iloc[0] - last_two["high"].iloc[1])
                high_avg = last_two["high"].mean()
                if high_avg > 0 and high_diff / high_avg < 0.02:
                    df.loc[df.index[i], "double_top"] = True

            if len(low_points) >= 2:
                last_two = low_points.iloc[-2:]
                low_diff = abs(last_two["low"].iloc[0] - last_two["low"].iloc[1])
                low_avg = last_two["low"].mean()
                if low_avg > 0 and low_diff / low_avg < 0.02:
                    df.loc[df.index[i], "double_bottom"] = True

            if len(high_points) >= 3:
                last_three = high_points.iloc[-3:]
                h1, h2, h3 = last_three["high"].iloc[0], last_three["high"].iloc[1], last_three["high"].iloc[2]
                if h2 > h1 and h2 > h3:
                    df.loc[df.index[i], "head_shoulders"] = True

            if len(low_points) >= 3:
                last_three = low_points.iloc[-3:]
                l1, l2, l3 = last_three["low"].iloc[0], last_three["low"].iloc[1], last_three["low"].iloc[2]
                if l2 < l1 and l2 < l3:
                    df.loc[df.index[i], "inverse_head_shoulders"] = True

        return df

    def get_price_action_score(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0

        last = df.iloc[-1]
        score = 0.0

        if last.get("bullish_engulfing"):
            score += 10
        if last.get("bearish_engulfing"):
            score -= 10
        if last.get("hammer"):
            score += 8
        if last.get("shooting_star"):
            score -= 8
        if last.get("morning_star"):
            score += 12
        if last.get("evening_star"):
            score -= 12
        if last.get("double_bottom"):
            score += 10
        if last.get("double_top"):
            score -= 10
        if last.get("inverse_head_shoulders"):
            score += 15
        if last.get("head_shoulders"):
            score -= 15

        return score
