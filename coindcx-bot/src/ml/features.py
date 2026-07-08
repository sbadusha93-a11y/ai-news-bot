from typing import List

import numpy as np
import pandas as pd
from loguru import logger


class FeatureEngineer:
    def __init__(self):
        self.feature_columns = []

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 100:
            return pd.DataFrame()

        df = df.copy()
        features = pd.DataFrame(index=df.index)

        features["rsi"] = df.get("rsi", 50)
        features["stoch_rsi"] = df.get("stoch_rsi", 50)
        features["macd"] = df.get("macd", 0)
        features["macd_histogram"] = df.get("macd_histogram", 0)
        features["adx"] = df.get("adx", 25)

        for period in [9, 20, 50, 100, 200]:
            col = f"ema_{period}"
            if col in df.columns:
                features[f"price_to_{col}"] = df["close"] / df[col].replace(0, np.nan) - 1

        features["atr_percent"] = df.get("atr_percent", 0)
        features["bb_position"] = df.get("bb_position", 0.5)
        features["volume_ratio"] = df.get("volume_spike_ratio", 1)
        features["mfi"] = df.get("mfi", 50)
        features["cmf"] = df.get("cmf", 0)
        features["obv_signal_binary"] = (df.get("obv_signal", "neutral") == "bullish").astype(int)
        features["cci"] = df.get("cci", 0)

        features["close_return_1"] = df["close"].pct_change(1)
        features["close_return_5"] = df["close"].pct_change(5)
        features["close_return_20"] = df["close"].pct_change(20)
        features["volatility_20"] = df["close"].pct_change().rolling(20).std()

        features["high_low_ratio"] = df["high"] / df["low"].replace(0, np.nan)
        features["close_open_ratio"] = df["close"] / df["open"].replace(0, np.nan)

        features["smc_bos_bullish"] = (df.get("bos", "none") == "bullish_bos").astype(int)
        features["smc_bos_bearish"] = (df.get("bos", "none") == "bearish_bos").astype(int)
        features["smc_choch_bullish"] = (df.get("choch", "none") == "bullish_choch").astype(int)
        features["smc_choch_bearish"] = (df.get("choch", "none") == "bearish_choch").astype(int)
        features["fvg_bullish"] = (df.get("fvg", "none") == "bullish_fvg").astype(int)
        features["fvg_bearish"] = (df.get("fvg", "none") == "bearish_fvg").astype(int)

        features["target"] = self._create_target(df)

        self.feature_columns = [c for c in features.columns if c != "target"]
        features = features.dropna()
        features = features.dropna(subset=["target"])
        return features

    def _create_target(self, df: pd.DataFrame, horizon: int = 12) -> pd.Series:
        future_returns = df["close"].shift(-horizon) / df["close"] - 1
        target = pd.Series(0, index=df.index)
        target[future_returns > 0.02] = 1
        target[future_returns < -0.02] = -1
        return target

    def get_feature_names(self) -> List[str]:
        return self.feature_columns
