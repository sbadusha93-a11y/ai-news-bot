import numpy as np
import pandas as pd
from loguru import logger


class SMCIndicators:
    """Smart Money Concepts (SMC) Indicators"""

    def __init__(self):
        self.swing_lookback = 5
        self.fvg_tolerance = 0.001

    def compute_all(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 50:
            return df

        df = df.copy()
        df = self._swing_points(df)
        df = self._break_of_structure(df)
        df = self._change_of_character(df)
        df = self._order_blocks(df)
        df = self._fair_value_gaps(df)
        df = self._liquidity_zones(df)
        df = self._institutional_zones(df)
        df = self._mitigation_blocks(df)
        df = self._breaker_blocks(df)
        df = self._premium_discount_zones(df)
        df = self._equal_highs_lows(df)
        df = self._stop_hunt(df)
        df = self._liquidity_grab(df)
        df = self._liquidity_pools(df)

        return df

    def _swing_points(self, df: pd.DataFrame) -> pd.DataFrame:
        lb = self.swing_lookback
        df["swing_high"] = False
        df["swing_low"] = False

        for i in range(lb, len(df) - lb):
            if all(df["high"].iloc[i] >= df["high"].iloc[i - j] for j in range(1, lb + 1)) and \
               all(df["high"].iloc[i] >= df["high"].iloc[i + j] for j in range(1, lb + 1)):
                df.loc[df.index[i], "swing_high"] = True

            if all(df["low"].iloc[i] <= df["low"].iloc[i - j] for j in range(1, lb + 1)) and \
               all(df["low"].iloc[i] <= df["low"].iloc[i + j] for j in range(1, lb + 1)):
                df.loc[df.index[i], "swing_low"] = True

        return df

    def _break_of_structure(self, df: pd.DataFrame) -> pd.DataFrame:
        df["bos"] = "none"
        df["bos_type"] = "none"

        swing_highs = df[df["swing_high"]].index
        swing_lows = df[df["swing_low"]].index

        if len(swing_highs) >= 2:
            last_high_idx = swing_highs[-1]
            prev_high_idx = swing_highs[-2]
            if df.loc[last_high_idx, "high"] > df.loc[prev_high_idx, "high"]:
                df.loc[last_high_idx:, "bos"] = "bullish_bos"
                df.loc[last_high_idx:, "bos_type"] = "structure_break_up"

        if len(swing_lows) >= 2:
            last_low_idx = swing_lows[-1]
            prev_low_idx = swing_lows[-2]
            if df.loc[last_low_idx, "low"] < df.loc[prev_low_idx, "low"]:
                df.loc[last_low_idx:, "bos"] = "bearish_bos"
                df.loc[last_low_idx:, "bos_type"] = "structure_break_down"

        return df

    def _change_of_character(self, df: pd.DataFrame) -> pd.DataFrame:
        df["choch"] = "none"

        for i in range(10, len(df)):
            recent_highs = df["high"].iloc[i - 10:i]
            recent_lows = df["low"].iloc[i - 10:i]
            prev_trend = "bullish" if df["close"].iloc[i - 10] < df["close"].iloc[i - 1] else "bearish"

            if prev_trend == "bullish":
                if df["close"].iloc[i] < recent_lows.min():
                    df.loc[df.index[i], "choch"] = "bearish_choch"
            else:
                if df["close"].iloc[i] > recent_highs.max():
                    df.loc[df.index[i], "choch"] = "bullish_choch"

        return df

    def _order_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        df["order_block"] = "none"
        df["ob_type"] = "none"

        for i in range(3, len(df)):
            if df["close"].iloc[i] > df["close"].iloc[i - 1] and \
               df["close"].iloc[i - 1] < df["close"].iloc[i - 2]:
                df.loc[df.index[i], "order_block"] = "bullish_ob"
                df.loc[df.index[i], "ob_type"] = "demand"
                df.loc[df.index[i], "ob_high"] = df["high"].iloc[i - 1]
                df.loc[df.index[i], "ob_low"] = df["low"].iloc[i - 1]

            elif df["close"].iloc[i] < df["close"].iloc[i - 1] and \
                 df["close"].iloc[i - 1] > df["close"].iloc[i - 2]:
                df.loc[df.index[i], "order_block"] = "bearish_ob"
                df.loc[df.index[i], "ob_type"] = "supply"
                df.loc[df.index[i], "ob_high"] = df["high"].iloc[i - 1]
                df.loc[df.index[i], "ob_low"] = df["low"].iloc[i - 1]

        return df

    def _fair_value_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        df["fvg"] = "none"
        df["fvg_type"] = "none"
        df["fvg_top"] = 0.0
        df["fvg_bottom"] = 0.0

        for i in range(2, len(df)):
            if df["low"].iloc[i] > df["high"].iloc[i - 2]:
                df.loc[df.index[i], "fvg"] = "bullish_fvg"
                df.loc[df.index[i], "fvg_type"] = "upward"
                df.loc[df.index[i], "fvg_bottom"] = df["high"].iloc[i - 2]
                df.loc[df.index[i], "fvg_top"] = df["low"].iloc[i]

            elif df["high"].iloc[i] < df["low"].iloc[i - 2]:
                df.loc[df.index[i], "fvg"] = "bearish_fvg"
                df.loc[df.index[i], "fvg_type"] = "downward"
                df.loc[df.index[i], "fvg_top"] = df["low"].iloc[i - 2]
                df.loc[df.index[i], "fvg_bottom"] = df["high"].iloc[i]

        return df

    def _liquidity_zones(self, df: pd.DataFrame) -> pd.DataFrame:
        df["liquidity_zone"] = "none"
        lookback = 20

        for i in range(lookback, len(df)):
            window_high = df["high"].iloc[i - lookback:i]
            window_low = df["low"].iloc[i - lookback:i]
            current_high = df["high"].iloc[i]
            current_low = df["low"].iloc[i]

            if current_high > window_high.max():
                df.loc[df.index[i], "liquidity_zone"] = "above"
            elif current_low < window_low.min():
                df.loc[df.index[i], "liquidity_zone"] = "below"

        return df

    def _institutional_zones(self, df: pd.DataFrame) -> pd.DataFrame:
        df["institutional_zone"] = "none"

        for i in range(10, len(df)):
            if df["volume"].iloc[i] > df["volume"].iloc[i - 10:i].mean() * 2:
                candle_range = df["high"].iloc[i] - df["low"].iloc[i]
                if df["close"].iloc[i] > df["open"].iloc[i]:
                    zone_top = df["close"].iloc[i]
                    zone_bottom = df["close"].iloc[i] - candle_range * 0.5
                    df.loc[df.index[i], "institutional_zone"] = "demand"
                else:
                    zone_top = df["close"].iloc[i] + candle_range * 0.5
                    zone_bottom = df["close"].iloc[i]
                    df.loc[df.index[i], "institutional_zone"] = "supply"

        return df

    def _mitigation_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        df["mitigation_block"] = "none"

        for i in range(5, len(df)):
            if df["order_block"].iloc[i] != "none" and df["order_block"].iloc[i - 1] != "none":
                if df["close"].iloc[i] > df["high"].iloc[i - 1]:
                    df.loc[df.index[i], "mitigation_block"] = "bullish_mitigation"

        return df

    def _breaker_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        df["breaker_block"] = "none"

        for i in range(5, len(df)):
            if df["bos"].iloc[i] == "bearish_bos" and df["bos"].iloc[i - 1] == "bullish_bos":
                df.loc[df.index[i], "breaker_block"] = "bearish_breaker"
            elif df["bos"].iloc[i] == "bullish_bos" and df["bos"].iloc[i - 1] == "bearish_bos":
                df.loc[df.index[i], "breaker_block"] = "bullish_breaker"

        return df

    def _premium_discount_zones(self, df: pd.DataFrame) -> pd.DataFrame:
        df["premium_zone"] = False
        df["discount_zone"] = False
        lookback = 50

        for i in range(lookback, len(df)):
            high = df["high"].iloc[i - lookback:i].max()
            low = df["low"].iloc[i - lookback:i].min()
            mid = (high + low) / 2

            if df["close"].iloc[i] > mid:
                df.loc[df.index[i], "premium_zone"] = True
            else:
                df.loc[df.index[i], "discount_zone"] = True

        return df

    def _equal_highs_lows(self, df: pd.DataFrame) -> pd.DataFrame:
        df["equal_high"] = False
        df["equal_low"] = False
        tolerance = 0.001

        for i in range(5, len(df)):
            for j in range(1, 6):
                if abs(df["high"].iloc[i] - df["high"].iloc[i - j]) / df["high"].iloc[i] < tolerance:
                    df.loc[df.index[i], "equal_high"] = True
                if abs(df["low"].iloc[i] - df["low"].iloc[i - j]) / df["low"].iloc[i] < tolerance:
                    df.loc[df.index[i], "equal_low"] = True

        return df

    def _stop_hunt(self, df: pd.DataFrame) -> pd.DataFrame:
        df["stop_hunt"] = "none"

        for i in range(5, len(df)):
            if df["swing_low"].iloc[i - 1] and \
               df["low"].iloc[i] < df["low"].iloc[i - 1] and \
               df["close"].iloc[i] > df["low"].iloc[i - 1]:
                df.loc[df.index[i], "stop_hunt"] = "bullish_stop_hunt"

            elif df["swing_high"].iloc[i - 1] and \
                 df["high"].iloc[i] > df["high"].iloc[i - 1] and \
                 df["close"].iloc[i] < df["high"].iloc[i - 1]:
                df.loc[df.index[i], "stop_hunt"] = "bearish_stop_hunt"

        return df

    def _liquidity_grab(self, df: pd.DataFrame) -> pd.DataFrame:
        df["liquidity_grab"] = "none"

        for i in range(10, len(df)):
            prev_range = df["high"].iloc[i - 5:i].max() - df["low"].iloc[i - 5:i].min()
            current_range = df["high"].iloc[i] - df["low"].iloc[i]

            if current_range > prev_range * 1.5:
                if df["close"].iloc[i] > df["open"].iloc[i] and \
                   df["low"].iloc[i] < df["low"].iloc[i - 5:i].min():
                    df.loc[df.index[i], "liquidity_grab"] = "bullish_grab"
                elif df["close"].iloc[i] < df["open"].iloc[i] and \
                     df["high"].iloc[i] > df["high"].iloc[i - 5:i].max():
                    df.loc[df.index[i], "liquidity_grab"] = "bearish_grab"

        return df

    def _liquidity_pools(self, df: pd.DataFrame) -> pd.DataFrame:
        df["liquidity_pool_high"] = 0.0
        df["liquidity_pool_low"] = 0.0
        lookback = 30
        tolerance = 0.002

        for i in range(lookback, len(df)):
            pool_high_count = 0
            pool_low_count = 0
            weighted_high = 0.0
            weighted_low = 0.0

            for j in range(i - lookback, i):
                if df["volume"].iloc[j] > df["volume"].iloc[i - lookback:i].mean():
                    if df["close"].iloc[j] > df["open"].iloc[j]:
                        pool_high_count += 1
                        weighted_high += df["high"].iloc[j] * df["volume"].iloc[j]
                    else:
                        pool_low_count += 1
                        weighted_low += df["low"].iloc[j] * df["volume"].iloc[j]

            if pool_high_count > 3:
                df.loc[df.index[i], "liquidity_pool_high"] = \
                    weighted_high / sum(
                        df["volume"].iloc[j]
                        for j in range(i - lookback, i)
                        if df["close"].iloc[j] > df["open"].iloc[j]
                        and df["volume"].iloc[j] > df["volume"].iloc[i - lookback:i].mean()
                    )

            if pool_low_count > 3:
                df.loc[df.index[i], "liquidity_pool_low"] = \
                    weighted_low / sum(
                        df["volume"].iloc[j]
                        for j in range(i - lookback, i)
                        if df["close"].iloc[j] < df["open"].iloc[j]
                        and df["volume"].iloc[j] > df["volume"].iloc[i - lookback:i].mean()
                    )

        return df

    def get_smc_score(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0

        last = df.iloc[-1]
        score = 0.0

        if last.get("bos") == "bullish_bos":
            score += 15
        elif last.get("bos") == "bearish_bos":
            score -= 15

        if last.get("choch") == "bullish_choch":
            score += 10
        elif last.get("choch") == "bearish_choch":
            score -= 10

        if last.get("order_block") == "bullish_ob":
            score += 8
        elif last.get("order_block") == "bearish_ob":
            score -= 8

        if last.get("fvg") == "bullish_fvg":
            score += 6
        elif last.get("fvg") == "bearish_fvg":
            score -= 6

        if last.get("stop_hunt") == "bullish_stop_hunt":
            score += 10
        elif last.get("stop_hunt") == "bearish_stop_hunt":
            score -= 10

        if last.get("liquidity_grab") == "bullish_grab":
            score += 8
        elif last.get("liquidity_grab") == "bearish_grab":
            score -= 8

        if last.get("mitigation_block") == "bullish_mitigation":
            score += 5

        if last.get("breaker_block") == "bullish_breaker":
            score += 7
        elif last.get("breaker_block") == "bearish_breaker":
            score -= 7

        if last.get("premium_zone"):
            score -= 5
        if last.get("discount_zone"):
            score += 5

        if last.get("institutional_zone") == "demand":
            score += 8
        elif last.get("institutional_zone") == "supply":
            score -= 8

        return score
