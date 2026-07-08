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

        try:
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
        except Exception as e:
            logger.warning(f"SMC computation failed: {e}")
            defaults = {
                "bos": "none", "bos_type": "none", "choch": "none",
                "order_block": "none", "ob_type": "none", "ob_high": 0.0, "ob_low": 0.0,
                "fvg": "none", "fvg_type": "none", "fvg_top": 0.0, "fvg_bottom": 0.0,
                "liquidity_zone": "none", "institutional_zone": "none",
                "mitigation_block": "none", "breaker_block": "none",
                "premium_zone": False, "discount_zone": False,
                "equal_high": False, "equal_low": False, "stop_hunt": "none",
                "liquidity_grab": "none", "liquidity_pool_high": 0.0, "liquidity_pool_low": 0.0,
            }
            for col, val in defaults.items():
                if col not in df.columns:
                    df[col] = val

        return df

    def _swing_points(self, df: pd.DataFrame) -> pd.DataFrame:
        lb = self.swing_lookback
        n = len(df)
        df["swing_high"] = False
        df["swing_low"] = False

        h = df["high"].values
        lo = df["low"].values
        sh = np.zeros(n, dtype=bool)
        sl = np.zeros(n, dtype=bool)

        for i in range(lb, n - lb):
            sh[i] = h[i] >= h[i - lb:i].max() and h[i] >= h[i + 1:i + lb + 1].max()
            sl[i] = lo[i] <= lo[i - lb:i].min() and lo[i] <= lo[i + 1:i + lb + 1].min()

        df["swing_high"] = sh
        df["swing_low"] = sl
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

        close_vals = df["close"].values
        high_vals = df["high"].values
        low_vals = df["low"].values
        idx = df.index

        for i in range(10, len(df)):
            prev_trend = "bullish" if close_vals[i - 10] < close_vals[i - 1] else "bearish"

            if prev_trend == "bullish":
                if close_vals[i] < low_vals[i - 10:i].min():
                    df.loc[idx[i], "choch"] = "bearish_choch"
            else:
                if close_vals[i] > high_vals[i - 10:i].max():
                    df.loc[idx[i], "choch"] = "bullish_choch"

        return df

    def _order_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        df["order_block"] = "none"
        df["ob_type"] = "none"

        c = df["close"].values
        h = df["high"].values
        lo = df["low"].values
        ob = np.full(len(df), "none", dtype=object)
        ob_type = np.full(len(df), "none", dtype=object)
        ob_high = np.zeros(len(df))
        ob_low = np.zeros(len(df))

        for i in range(3, len(df)):
            if c[i] > c[i - 1] and c[i - 1] < c[i - 2]:
                ob[i] = "bullish_ob"
                ob_type[i] = "demand"
                ob_high[i] = h[i - 1]
                ob_low[i] = lo[i - 1]
            elif c[i] < c[i - 1] and c[i - 1] > c[i - 2]:
                ob[i] = "bearish_ob"
                ob_type[i] = "supply"
                ob_high[i] = h[i - 1]
                ob_low[i] = lo[i - 1]

        df["order_block"] = ob
        df["ob_type"] = ob_type
        df["ob_high"] = ob_high
        df["ob_low"] = ob_low
        return df

    def _fair_value_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        df["fvg"] = "none"
        df["fvg_type"] = "none"
        df["fvg_top"] = 0.0
        df["fvg_bottom"] = 0.0

        h = df["high"].values
        lo = df["low"].values
        fvg = np.full(len(df), "none", dtype=object)
        fvg_type = np.full(len(df), "none", dtype=object)
        fvg_top = np.zeros(len(df))
        fvg_bottom = np.zeros(len(df))

        for i in range(2, len(df)):
            if lo[i] > h[i - 2]:
                fvg[i] = "bullish_fvg"
                fvg_type[i] = "upward"
                fvg_bottom[i] = h[i - 2]
                fvg_top[i] = lo[i]
            elif h[i] < lo[i - 2]:
                fvg[i] = "bearish_fvg"
                fvg_type[i] = "downward"
                fvg_top[i] = lo[i - 2]
                fvg_bottom[i] = h[i]

        df["fvg"] = fvg
        df["fvg_type"] = fvg_type
        df["fvg_top"] = fvg_top
        df["fvg_bottom"] = fvg_bottom
        return df

    def _liquidity_zones(self, df: pd.DataFrame) -> pd.DataFrame:
        df["liquidity_zone"] = "none"
        lookback = 20

        h = df["high"].values
        lo = df["low"].values
        lz = np.full(len(df), "none", dtype=object)

        for i in range(lookback, len(df)):
            if h[i] > h[i - lookback:i].max():
                lz[i] = "above"
            elif lo[i] < lo[i - lookback:i].min():
                lz[i] = "below"

        df["liquidity_zone"] = lz
        return df

    def _institutional_zones(self, df: pd.DataFrame) -> pd.DataFrame:
        df["institutional_zone"] = "none"

        v = df["volume"].values
        h = df["high"].values
        lo = df["low"].values
        c = df["close"].values
        o = df["open"].values
        iz = np.full(len(df), "none", dtype=object)

        for i in range(10, len(df)):
            if v[i] > v[i - 10:i].mean() * 2:
                candle_range = h[i] - lo[i]
                iz[i] = "demand" if c[i] > o[i] else "supply"

        df["institutional_zone"] = iz
        return df

    def _mitigation_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        ob = df["order_block"].values
        c = df["close"].values
        h = df["high"].values
        mb = np.full(len(df), "none", dtype=object)

        for i in range(5, len(df)):
            if ob[i] != "none" and ob[i - 1] != "none" and c[i] > h[i - 1]:
                mb[i] = "bullish_mitigation"

        df["mitigation_block"] = mb
        return df

    def _breaker_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        bos = df["bos"].values
        bb = np.full(len(df), "none", dtype=object)

        for i in range(5, len(df)):
            if bos[i] == "bearish_bos" and bos[i - 1] == "bullish_bos":
                bb[i] = "bearish_breaker"
            elif bos[i] == "bullish_bos" and bos[i - 1] == "bearish_bos":
                bb[i] = "bullish_breaker"

        df["breaker_block"] = bb
        return df

    def _premium_discount_zones(self, df: pd.DataFrame) -> pd.DataFrame:
        df["premium_zone"] = False
        df["discount_zone"] = False
        lookback = 50

        h = df["high"].values
        lo = df["low"].values
        c = df["close"].values
        pz = np.zeros(len(df), dtype=bool)
        dz = np.zeros(len(df), dtype=bool)

        for i in range(lookback, len(df)):
            mid = (h[i - lookback:i].max() + lo[i - lookback:i].min()) / 2
            if c[i] > mid:
                pz[i] = True
            else:
                dz[i] = True

        df["premium_zone"] = pz
        df["discount_zone"] = dz
        return df

    def _equal_highs_lows(self, df: pd.DataFrame) -> pd.DataFrame:
        df["equal_high"] = False
        df["equal_low"] = False
        tolerance = 0.001

        h = df["high"].values
        lo = df["low"].values
        eh = np.zeros(len(df), dtype=bool)
        el = np.zeros(len(df), dtype=bool)

        for i in range(5, len(df)):
            hits_high = 0
            hits_low = 0
            for j in range(1, 6):
                if abs(h[i] - h[i - j]) / max(h[i], 1e-10) < tolerance:
                    hits_high += 1
                if abs(lo[i] - lo[i - j]) / max(lo[i], 1e-10) < tolerance:
                    hits_low += 1
            eh[i] = hits_high >= 3
            el[i] = hits_low >= 3

        df["equal_high"] = eh
        df["equal_low"] = el
        return df

    def _stop_hunt(self, df: pd.DataFrame) -> pd.DataFrame:
        sh = np.full(len(df), "none", dtype=object)

        sl = df["swing_low"].values
        shigh = df["swing_high"].values
        lo = df["low"].values
        h = df["high"].values
        c = df["close"].values

        for i in range(5, len(df)):
            if sl[i - 1] and lo[i] < lo[i - 1] and c[i] > lo[i - 1]:
                sh[i] = "bullish_stop_hunt"
            elif shigh[i - 1] and h[i] > h[i - 1] and c[i] < h[i - 1]:
                sh[i] = "bearish_stop_hunt"

        df["stop_hunt"] = sh
        return df

    def _liquidity_grab(self, df: pd.DataFrame) -> pd.DataFrame:
        lg = np.full(len(df), "none", dtype=object)

        h = df["high"].values
        lo = df["low"].values
        c = df["close"].values
        o = df["open"].values

        for i in range(10, len(df)):
            prev_max = h[i - 5:i].max()
            prev_min = lo[i - 5:i].min()
            prev_range = prev_max - prev_min
            current_range = h[i] - lo[i]

            if current_range > prev_range * 1.5:
                if c[i] > o[i] and lo[i] < prev_min:
                    lg[i] = "bullish_grab"
                elif c[i] < o[i] and h[i] > prev_max:
                    lg[i] = "bearish_grab"

        df["liquidity_grab"] = lg
        return df

    def _liquidity_pools(self, df: pd.DataFrame) -> pd.DataFrame:
        df["liquidity_pool_high"] = 0.0
        df["liquidity_pool_low"] = 0.0
        lookback = 30

        v = df["volume"].values
        o = df["open"].values
        h = df["high"].values
        lo = df["low"].values
        c = df["close"].values
        idx = df.index

        for i in range(lookback, len(df)):
            start = i - lookback
            window_vol = v[start:i]
            mean_vol = window_vol.mean()

            pool_high_count = 0
            pool_low_count = 0
            weighted_high = 0.0
            weighted_low = 0.0
            vol_sum_high = 0.0
            vol_sum_low = 0.0

            for j in range(start, i):
                if v[j] <= mean_vol:
                    continue
                if c[j] > o[j]:
                    pool_high_count += 1
                    weighted_high += h[j] * v[j]
                    vol_sum_high += v[j]
                else:
                    pool_low_count += 1
                    weighted_low += lo[j] * v[j]
                    vol_sum_low += v[j]

            if pool_high_count > 3 and vol_sum_high > 0:
                df.loc[idx[i], "liquidity_pool_high"] = weighted_high / vol_sum_high

            if pool_low_count > 3 and vol_sum_low > 0:
                df.loc[idx[i], "liquidity_pool_low"] = weighted_low / vol_sum_low

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
