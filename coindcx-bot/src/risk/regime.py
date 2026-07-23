import json
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
from loguru import logger


class MarketPhase(Enum):
    ACCUMULATION = "accumulation"
    MARKUP = "markup"
    DISTRIBUTION = "distribution"
    MARKDOWN = "markdown"


class VolatilityRegime(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    EXTREME = "extreme"


class TrendRegime(Enum):
    STRONG_UPTREND = "strong_uptrend"
    WEAK_UPTREND = "weak_uptrend"
    SIDEWAYS = "sideways"
    WEAK_DOWNTREND = "weak_downtrend"
    STRONG_DOWNTREND = "strong_downtrend"


class MarketRegimeDetector:
    def __init__(self):
        self.regime_history: Dict[str, str] = {}
        self._adx_lookback = 50
        self._vol_lookback = 30
        self._phase_lookback = 200

    def detect(self, df: pd.DataFrame) -> Dict:
        if df.empty or len(df) < 100:
            return self._neutral_regime()

        trend = self._detect_trend_regime(df)
        volatility = self._detect_volatility_regime(df)
        phase = self._detect_market_phase(df)
        strength = self._detect_trend_strength(df)

        regime = {
            "trend": trend.value,
            "volatility": volatility.value,
            "phase": phase.value,
            "strength": strength,
            "is_tradeable": self._is_tradeable(trend, volatility),
            "adx": float(df["adx"].iloc[-1]) if "adx" in df.columns else 0,
            "atr_percent": float(df["atr_percent"].iloc[-1]) if "atr_percent" in df.columns else 0,
        }
        return regime

    def _neutral_regime(self) -> Dict:
        return {
            "trend": "sideways",
            "volatility": "normal",
            "phase": "accumulation",
            "strength": 0.0,
            "is_tradeable": True,
            "adx": 0,
            "atr_percent": 0,
        }

    def _detect_trend_regime(self, df: pd.DataFrame) -> TrendRegime:
        last = df.iloc[-1]
        adx = last.get("adx", 0)
        close = last["close"]
        ema_50 = last.get("ema_50", close)
        ema_200 = last.get("ema_200", close)

        above_50 = close > ema_50
        above_200 = close > ema_200
        ema_aligned = ema_50 > ema_200 if above_50 else ema_50 < ema_200

        if above_50 and above_200 and ema_aligned and adx > 25:
            return TrendRegime.STRONG_UPTREND
        if not above_50 and not above_200 and ema_aligned and adx > 25:
            return TrendRegime.STRONG_DOWNTREND
        if above_50 and above_200:
            return TrendRegime.WEAK_UPTREND
        if not above_50 and not above_200:
            return TrendRegime.WEAK_DOWNTREND
        return TrendRegime.SIDEWAYS

    def _detect_volatility_regime(self, df: pd.DataFrame) -> VolatilityRegime:
        atr_pct = df["atr_percent"] if "atr_percent" in df.columns else df["close"].pct_change().abs() * 100
        recent = atr_pct.iloc[-self._vol_lookback:]
        median_vol = recent.median()
        current = atr_pct.iloc[-1] if isinstance(atr_pct, pd.Series) else atr_pct

        if current > median_vol * 3:
            return VolatilityRegime.EXTREME
        if current > median_vol * 1.5:
            return VolatilityRegime.HIGH
        if current < median_vol * 0.5:
            return VolatilityRegime.LOW
        return VolatilityRegime.NORMAL

    def _detect_market_phase(self, df: pd.DataFrame) -> MarketPhase:
        if len(df) < self._phase_lookback:
            return MarketPhase.ACCUMULATION

        prices = df["close"].values
        chunk = self._phase_lookback
        third = chunk // 3

        p1 = prices[-chunk:-chunk + third].mean()
        p2 = prices[-chunk + third:-chunk + 2 * third].mean()
        p3 = prices[-chunk + third:].mean()

        if p1 < p2 > p3 and p3 < p2 * 0.95:
            return MarketPhase.DISTRIBUTION
        if p1 > p2 < p3 and p3 > p1:
            return MarketPhase.ACCUMULATION
        if p1 < p2 < p3:
            return MarketPhase.MARKUP
        if p1 > p2 > p3:
            return MarketPhase.MARKDOWN

        recent_high = prices[-third:].max()
        recent_low = prices[-third:].min()
        rng = recent_high - recent_low
        if rng / prices[-1] < 0.05:
            return MarketPhase.ACCUMULATION
        return MarketPhase.MARKUP if p3 > p1 else MarketPhase.MARKDOWN

    def _detect_trend_strength(self, df: pd.DataFrame) -> float:
        if "adx" not in df.columns:
            return 0.0
        adx = df["adx"].iloc[-min(self._adx_lookback, len(df)):]
        return float(adx.mean()) / 100.0 if adx.mean() > 0 else 0.0

    def _is_tradeable(self, trend: TrendRegime, vol: VolatilityRegime) -> bool:
        if vol == VolatilityRegime.EXTREME:
            return False
        if trend == TrendRegime.SIDEWAYS:
            return False
        return True

    def get_regime_adjusted_params(self, df: pd.DataFrame, base_params: Dict) -> Dict:
        regime = self.detect(df)
        params = dict(base_params)

        if regime["volatility"] == "high":
            params["stop_loss_atr_multiplier"] = base_params.get("stop_loss_atr_multiplier", 1.5) * 1.3
            params["trailing_stop_distance"] = base_params.get("trailing_stop_distance", 0.4) * 1.5
            params["break_even_trigger"] = base_params.get("break_even_trigger", 1.2) * 1.5
        elif regime["volatility"] == "low":
            params["stop_loss_atr_multiplier"] = base_params.get("stop_loss_atr_multiplier", 1.5) * 0.8
            params["trailing_stop_distance"] = base_params.get("trailing_stop_distance", 0.4) * 0.7
            params["break_even_trigger"] = base_params.get("break_even_trigger", 1.2) * 0.8
        elif regime["volatility"] == "extreme":
            params["max_risk_per_trade"] = base_params.get("max_risk_per_trade", 0.75) * 0.5

        if regime["trend"] in ("strong_uptrend", "strong_downtrend"):
            params["min_confidence"] = base_params.get("min_confidence", 85) * 0.9
        elif regime["trend"] == "sideways":
            params["min_confidence"] = base_params.get("min_confidence", 85) * 1.15

        return params
