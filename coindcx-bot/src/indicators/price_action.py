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
        safe_range = total_range.replace(0, np.nan)

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

            curr_range_safe = curr_range if curr_range > 0 else np.nan

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

            body_ratio = curr_body / curr_range_safe if not np.isnan(curr_range_safe) else 0
            uw_ratio = upper_wick.iloc[i] / curr_range_safe if not np.isnan(curr_range_safe) else 0
            lw_ratio = lower_wick.iloc[i] / curr_range_safe if not np.isnan(curr_range_safe) else 0

            if body_ratio < 0.3 and lw_ratio > 0.6 and uw_ratio < 0.1:
                df.loc[df.index[i], "hammer"] = True

            if body_ratio < 0.3 and uw_ratio > 0.6 and lw_ratio < 0.1:
                df.loc[df.index[i], "shooting_star"] = True

            if body_ratio < 0.1:
                df.loc[df.index[i], "doji"] = True

            if i >= 2:
                b1 = abs(df["close"].iloc[i - 2] - df["open"].iloc[i - 2])
                b2 = abs(df["close"].iloc[i - 1] - df["open"].iloc[i - 1])
                prev_range = df["high"].iloc[i - 1] - df["low"].iloc[i - 1]
                safe_prev_range = prev_range if prev_range > 0 else np.nan
                if df["close"].iloc[i - 2] < df["open"].iloc[i - 2] and \
                   (b2 / safe_prev_range if not np.isnan(safe_prev_range) else 1) < 0.1 and \
                   df["close"].iloc[i] > df["open"].iloc[i] and \
                   df["close"].iloc[i] > (df["high"].iloc[i - 2] + df["low"].iloc[i - 2]) / 2:
                    df.loc[df.index[i], "morning_star"] = True

                if df["close"].iloc[i - 2] > df["open"].iloc[i - 2] and \
                   (b2 / safe_prev_range if not np.isnan(safe_prev_range) else 1) < 0.1 and \
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
        if "swing_high" not in df.columns or "swing_low" not in df.columns:
            return df

        c = df["close"].values
        h = df["high"].values
        lo = df["low"].values
        sh = df["swing_high"].values
        sl = df["swing_low"].values
        idx = df.index
        lookback = 50

        for i in range(lookback, len(df)):
            start = i - lookback
            current_price = c[i]

            best_resistance = 0.0
            best_support = 0.0

            for j in range(start, i):
                if sh[j] and h[j] > current_price:
                    if best_resistance == 0 or h[j] < best_resistance:
                        best_resistance = h[j]
                if sl[j] and lo[j] < current_price:
                    if lo[j] > best_support:
                        best_support = lo[j]

            df.loc[idx[i], "resistance"] = best_resistance
            df.loc[idx[i], "support"] = best_support

        return df

    def _trendlines(self, df: pd.DataFrame) -> pd.DataFrame:
        df["uptrend_line"] = 0.0
        df["downtrend_line"] = 0.0
        lookback = 30

        lo = df["low"].values
        h = df["high"].values
        idx = df.index

        for i in range(lookback, len(df)):
            start = i - lookback
            lows = lo[start:i]
            highs = h[start:i]

            low_indices = np.where(
                (lows[1:-1] < lows[:-2]) & (lows[1:-1] < lows[2:])
            )[0]
            if len(low_indices) >= 2:
                a, b = low_indices[-2], low_indices[-1]
                slope = (lows[b] - lows[a]) / (b - a)
                df.loc[idx[i], "uptrend_line"] = lows[b] + slope * (lookback - b - 1)

            high_indices = np.where(
                (highs[1:-1] > highs[:-2]) & (highs[1:-1] > highs[2:])
            )[0]
            if len(high_indices) >= 2:
                a, b = high_indices[-2], high_indices[-1]
                slope = (highs[b] - highs[a]) / (b - a)
                df.loc[idx[i], "downtrend_line"] = highs[b] + slope * (lookback - b - 1)

        return df

    def _chart_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        df["double_top"] = False
        df["double_bottom"] = False
        df["head_shoulders"] = False
        df["inverse_head_shoulders"] = False
        if "swing_high" not in df.columns or "swing_low" not in df.columns:
            return df

        h = df["high"].values
        lo = df["low"].values
        sh = df["swing_high"].values
        sl = df["swing_low"].values
        idx = df.index
        lookback = 40

        swing_high_idx = [i for i in range(len(sh)) if sh[i]]
        swing_low_idx = [i for i in range(len(sl)) if sl[i]]

        for i in range(lookback, len(df)):
            start = i - lookback

            hi_in_window = [j for j in swing_high_idx if start <= j < i]
            if len(hi_in_window) >= 2:
                a, b = hi_in_window[-2], hi_in_window[-1]
                high_avg = (h[a] + h[b]) / 2
                if high_avg > 0 and abs(h[a] - h[b]) / high_avg < 0.02:
                    df.loc[idx[i], "double_top"] = True

            lo_in_window = [j for j in swing_low_idx if start <= j < i]
            if len(lo_in_window) >= 2:
                a, b = lo_in_window[-2], lo_in_window[-1]
                low_avg = (lo[a] + lo[b]) / 2
                if low_avg > 0 and abs(lo[a] - lo[b]) / low_avg < 0.02:
                    df.loc[idx[i], "double_bottom"] = True

            if len(hi_in_window) >= 3:
                a, b, c = hi_in_window[-3], hi_in_window[-2], hi_in_window[-1]
                if h[b] > h[a] and h[b] > h[c]:
                    df.loc[idx[i], "head_shoulders"] = True

            if len(lo_in_window) >= 3:
                a, b, c = lo_in_window[-3], lo_in_window[-2], lo_in_window[-1]
                if lo[b] < lo[a] and lo[b] < lo[c]:
                    df.loc[idx[i], "inverse_head_shoulders"] = True

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
