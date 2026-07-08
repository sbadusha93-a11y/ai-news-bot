import numpy as np
import pandas as pd
from loguru import logger

from src.config import bot_config


class VolumeIndicators:
    def __init__(self):
        self.settings = bot_config["indicator_settings"]

    def compute_all(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 50:
            return df

        df = df.copy()
        df = self._obv(df)
        df = self._cmf(df)
        df = self._mfi(df)
        df = self._volume_oscillator(df)
        df = self._volume_spike(df)
        df = self._buying_selling_pressure(df)
        df = self._accumulation_distribution(df)
        df = self._volume_divergence(df)
        df = self._whale_activity(df)
        df = self._volume_profile(df)

        return df

    def _obv(self, df: pd.DataFrame) -> pd.DataFrame:
        obv = [0]
        for i in range(1, len(df)):
            if df["close"].iloc[i] > df["close"].iloc[i - 1]:
                obv.append(obv[-1] + df["volume"].iloc[i])
            elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
                obv.append(obv[-1] - df["volume"].iloc[i])
            else:
                obv.append(obv[-1])
        df["obv"] = obv
        df["obv_ema"] = df["obv"].ewm(span=20).mean()
        df["obv_signal"] = np.where(
            df["obv"] > df["obv_ema"], "bullish", "bearish"
        )
        return df

    def _cmf(self, df: pd.DataFrame) -> pd.DataFrame:
        period = self.settings["cmf_period"]
        mfv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / \
              (df["high"] - df["low"]).replace(0, np.nan) * df["volume"]
        df["cmf"] = mfv.rolling(window=period).sum() / \
                    df["volume"].rolling(window=period).sum().replace(0, np.nan)
        df["cmf_signal"] = np.where(
            df["cmf"] > 0.05, "bullish",
            np.where(df["cmf"] < -0.05, "bearish", "neutral")
        )
        return df

    def _mfi(self, df: pd.DataFrame) -> pd.DataFrame:
        period = self.settings["mfi_period"]
        tp = (df["high"] + df["low"] + df["close"]) / 3
        rmf = tp * df["volume"]
        flow_positive = rmf.where(tp > tp.shift(1), 0).rolling(window=period).sum()
        flow_negative = rmf.where(tp < tp.shift(1), 0).rolling(window=period).sum()
        mfr = flow_positive / flow_negative.replace(0, np.nan)
        df["mfi"] = 100 - (100 / (1 + mfr))
        df["mfi_signal"] = np.where(
            df["mfi"] > 80, "overbought",
            np.where(df["mfi"] < 20, "oversold", "neutral")
        )
        return df

    def _volume_oscillator(self, df: pd.DataFrame) -> pd.DataFrame:
        fast = self.settings["volume_oscillator_fast"]
        slow = self.settings["volume_oscillator_slow"]
        fast_ma = df["volume"].ewm(span=fast).mean()
        slow_ma = df["volume"].ewm(span=slow).mean()
        df["volume_oscillator"] = ((fast_ma - slow_ma) / slow_ma.replace(0, np.nan)) * 100
        df["volume_oscillator_signal"] = np.where(
            df["volume_oscillator"] > 0, "expanding", "contracting"
        )
        return df

    def _volume_spike(self, df: pd.DataFrame) -> pd.DataFrame:
        lookback = 20
        df["volume_ma"] = df["volume"].rolling(window=lookback).mean()
        df["volume_std"] = df["volume"].rolling(window=lookback).std()
        df["volume_spike"] = df["volume"] > (df["volume_ma"] + 2 * df["volume_std"])
        df["volume_spike_ratio"] = df["volume"] / df["volume_ma"].replace(0, np.nan)
        df["volume_spike_type"] = np.where(
            df["volume_spike"], "spike", "normal"
        )
        return df

    def _buying_selling_pressure(self, df: pd.DataFrame) -> pd.DataFrame:
        df["buying_pressure"] = np.where(
            df["close"] > df["open"],
            df["volume"] * (df["close"] - df["open"]) / (df["high"] - df["low"]).replace(0, 1),
            0
        )
        df["selling_pressure"] = np.where(
            df["close"] < df["open"],
            df["volume"] * (df["open"] - df["close"]) / (df["high"] - df["low"]).replace(0, 1),
            0
        )
        df["buying_ratio"] = df["buying_pressure"] / \
            (df["buying_pressure"] + df["selling_pressure"]).replace(0, 1)
        df["pressure_signal"] = np.where(
            df["buying_ratio"] > 0.6, "strong_buying",
            np.where(df["buying_ratio"] < 0.4, "strong_selling", "neutral")
        )
        return df

    def _accumulation_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        clv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / \
              (df["high"] - df["low"]).replace(0, 1)
        df["ad_line"] = (clv * df["volume"]).cumsum()
        df["ad_ema"] = df["ad_line"].ewm(span=20).mean()
        df["ad_signal"] = np.where(
            df["ad_line"] > df["ad_ema"], "accumulation", "distribution"
        )
        return df

    def _volume_divergence(self, df: pd.DataFrame) -> pd.DataFrame:
        df["volume_divergence"] = "none"

        for i in range(20, len(df)):
            price_up = df["close"].iloc[i] > df["close"].iloc[i - 10]
            vol_down = df["volume"].iloc[i] < df["volume"].iloc[i - 10:i].mean()
            if price_up and vol_down:
                df.loc[df.index[i], "volume_divergence"] = "bearish_divergence"

            price_down = df["close"].iloc[i] < df["close"].iloc[i - 10]
            vol_up = df["volume"].iloc[i] > df["volume"].iloc[i - 10:i].mean()
            if price_down and vol_up:
                df.loc[df.index[i], "volume_divergence"] = "bullish_divergence"

        return df

    def _whale_activity(self, df: pd.DataFrame) -> pd.DataFrame:
        df["whale_activity"] = "none"
        lookback = 50

        for i in range(lookback, len(df)):
            recent_vol = df["volume"].iloc[i - lookback:i]
            mean_vol = recent_vol.mean()
            std_vol = recent_vol.std()
            current_vol = df["volume"].iloc[i]

            if current_vol > mean_vol + 3 * std_vol:
                candle_range = df["high"].iloc[i] - df["low"].iloc[i]
                avg_range = (df["high"].iloc[i - 5:i] - df["low"].iloc[i - 5:i]).mean()
                if candle_range > avg_range * 1.5:
                    if df["close"].iloc[i] > df["open"].iloc[i]:
                        df.loc[df.index[i], "whale_activity"] = "bullish_whale"
                    else:
                        df.loc[df.index[i], "whale_activity"] = "bearish_whale"

        return df

    def _volume_profile(self, df: pd.DataFrame) -> pd.DataFrame:
        df["volume_profile_poc"] = 0.0
        df["volume_profile_vah"] = 0.0
        df["volume_profile_val"] = 0.0

        if len(df) < 50:
            return df

        lookback = min(50, len(df))
        recent = df.iloc[-lookback:]

        if recent.empty or recent["close"].isna().all():
            return df

        price_bins = pd.cut(
            recent["close"],
            bins=20,
            labels=False,
            include_lowest=True,
        )
        vol_by_bin = recent.groupby(price_bins)["volume"].sum()
        if vol_by_bin.empty:
            return df
        poc_bin = vol_by_bin.idxmax()
        poc_prices = recent["close"].loc[
            price_bins.values == poc_bin
        ] if len(recent[price_bins.values == poc_bin]) > 0 else recent["close"]

        df.loc[df.index[-1], "volume_profile_poc"] = poc_prices.mean() if len(poc_prices) > 0 else recent["close"].iloc[-1]

        total_vol = vol_by_bin.sum()
        cum_vol = 0
        vah_price = recent["close"].iloc[-1]
        val_price = recent["close"].iloc[-1]

        max_bin = vol_by_bin.index.max()
        if pd.isna(max_bin):
            return df
        for bin_idx in range(int(max_bin), -1, -1):
            if bin_idx in vol_by_bin.index:
                cum_vol += vol_by_bin[bin_idx]
                if cum_vol >= total_vol * 0.3:
                    bin_prices = recent["close"].loc[price_bins == bin_idx]
                    vah_price = bin_prices.mean() if len(bin_prices) > 0 else recent["close"].iloc[-1]
                    break

        cum_vol = 0
        min_bin = vol_by_bin.index.min()
        if pd.isna(min_bin):
            return df
        for bin_idx in range(int(min_bin), int(max_bin) + 1):
            if bin_idx in vol_by_bin.index:
                cum_vol += vol_by_bin[bin_idx]
                if cum_vol >= total_vol * 0.3:
                    bin_prices = recent["close"].loc[price_bins == bin_idx]
                    val_price = bin_prices.mean() if len(bin_prices) > 0 else recent["close"].iloc[-1]
                    break

        df.loc[df.index[-1], "volume_profile_vah"] = vah_price
        df.loc[df.index[-1], "volume_profile_val"] = val_price

        return df

    def get_volume_score(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0

        last = df.iloc[-1]
        score = 0.0

        if last.get("obv_signal") == "bullish":
            score += 5
        elif last.get("obv_signal") == "bearish":
            score -= 5

        if last.get("cmf_signal") == "bullish":
            score += 8
        elif last.get("cmf_signal") == "bearish":
            score -= 8

        if last.get("mfi_signal") == "oversold":
            score += 6
        elif last.get("mfi_signal") == "overbought":
            score -= 6

        if last.get("volume_spike") and last.get("close", 0) > (df["close"].iloc[-2] if len(df) >= 2 else 0):
            score += 10
        elif last.get("volume_spike"):
            score -= 10

        if last.get("pressure_signal") == "strong_buying":
            score += 8
        elif last.get("pressure_signal") == "strong_selling":
            score -= 8

        if last.get("ad_signal") == "accumulation":
            score += 6
        elif last.get("ad_signal") == "distribution":
            score -= 6

        if last.get("volume_divergence") == "bullish_divergence":
            score += 10
        elif last.get("volume_divergence") == "bearish_divergence":
            score -= 10

        if last.get("whale_activity") == "bullish_whale":
            score += 12
        elif last.get("whale_activity") == "bearish_whale":
            score -= 12

        return score
