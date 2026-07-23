import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from loguru import logger

from src.config import bot_config
from src.exchange.coindcx import CoinDCXExchange
from src.indicators.technical import TechnicalIndicators
from src.indicators.smc import SMCIndicators
from src.indicators.volume import VolumeIndicators
from src.indicators.price_action import PriceActionIndicators
from src.indicators.sentiment import SentimentAnalyzer
from src.ml.predictor import MLPredictor
from src.risk.regime import MarketRegimeDetector
from src.strategy.scorer import TradeScorer


class StrategyEngine:
    def __init__(
        self,
        exchange: CoinDCXExchange,
        ml_predictor: Optional[MLPredictor] = None,
    ):
        self.exchange = exchange
        self.technical = TechnicalIndicators()
        self.smc = SMCIndicators()
        self.volume = VolumeIndicators()
        self.price_action = PriceActionIndicators()
        self.sentiment = SentimentAnalyzer()
        self.scorer = TradeScorer()
        self.ml_predictor = ml_predictor
        self.regime_detector = MarketRegimeDetector()
        self.timeframes = (
            [bot_config["timeframes"]["primary"]]
            + bot_config["timeframes"]["confirmation"]
        )
        self._weights = self._load_weights()

    def _load_weights(self) -> Dict:
        path = Path(__file__).parent.parent.parent / "config" / "weights.json"
        try:
            return json.loads(path.read_text())
        except Exception:
            logger.warning("Could not load weights.json, using defaults")
            return {}

    async def analyze_symbol(
        self, symbol: str, df_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        analysis = {
            "symbol": symbol,
            "timeframes": {},
            "overall": {},
            "signals": {},
            "regime": {},
        }

        for tf, df in df_dict.items():
            df = self.technical.compute_all(df)
            df = self.smc.compute_all(df)
            df = self.volume.compute_all(df)
            df = self.price_action.compute_all(df)

            regime = self.regime_detector.detect(df)
            base_params = bot_config["risk"]
            adjusted_risk = self.regime_detector.get_regime_adjusted_params(df, base_params)

            ml_score = 0.0
            ml_confidence = 0.0
            if self.ml_predictor is not None:
                try:
                    pred = self.ml_predictor.predict(df)
                    ml_confidence = pred.get("confidence", 0)
                    if pred.get("direction") == "long":
                        ml_score = ml_confidence * 20
                    elif pred.get("direction") == "short":
                        ml_score = -ml_confidence * 20
                except Exception:
                    pass

            last = df.iloc[-1] if not df.empty else pd.Series()
            technical_score = self._compute_weighted_technical_score(df)
            smc_score = self.smc.get_smc_score(df)
            volume_score = self.volume.get_volume_score(df)
            pa_score = self.price_action.get_price_action_score(df)

            analysis["timeframes"][tf] = {
                "last_row": last.to_dict() if not last.empty else {},
                "technical_score": technical_score,
                "smc_score": smc_score,
                "volume_score": volume_score,
                "price_action_score": pa_score,
                "ml_score": ml_score,
                "ml_confidence": ml_confidence,
                "trend": self._determine_trend(df),
                "regime": regime,
                "adjusted_risk": adjusted_risk,
                "support": last.get("support", 0),
                "resistance": last.get("resistance", 0),
            }

        primary_tf = bot_config["timeframes"]["primary"]
        analysis["regime"] = analysis["timeframes"].get(
            primary_tf, next(iter(analysis["timeframes"].values()), {})
        ).get("regime", {})

        analysis["overall"] = self._compute_overall_analysis(analysis["timeframes"])
        analysis["signals"] = self.scorer.compute_signals(analysis)

        regime = analysis["regime"]
        if regime.get("volatility") == "extreme" and not regime.get("is_tradeable", True):
            analysis["signals"]["is_tradeable"] = False
            analysis["signals"]["confidence"] = 0
            analysis["signals"]["reason"] = "Extreme volatility — trading paused"

        return analysis

    def _compute_weighted_technical_score(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0
        last = df.iloc[-1]
        score = 0.0
        w = self._weights.get("indicators", {})

        rsi = last.get("rsi", 50)
        if rsi < 30:
            score += 8 * w.get("rsi", 3) / 3
        elif rsi > 70:
            score -= 8 * w.get("rsi", 3) / 3

        if last.get("macd_signal_line") == "bullish":
            score += 10 * w.get("macd", 4) / 4
        elif last.get("macd_signal_line") == "bearish":
            score -= 10 * w.get("macd", 4) / 4

        if last.get("macd_histogram_signal") == "increasing":
            score += 5 * w.get("macd_histogram", 3) / 3
        else:
            score -= 5 * w.get("macd_histogram", 3) / 3

        if last.get("ema_9_20_cross") == "bullish":
            score += 6
        elif last.get("ema_9_20_cross") == "bearish":
            score -= 6

        ema_20_val = w.get("ema_20", 3)
        if last.get("ema_20_50_cross") == "bullish":
            score += 6 * ema_20_val / 3
        elif last.get("ema_20_50_cross") == "bearish":
            score -= 6 * ema_20_val / 3

        ema_50_val = w.get("ema_50", 3)
        if last.get("ema_50_100_cross") == "bullish":
            score += 4 * ema_50_val / 3
        elif last.get("ema_50_100_cross") == "bearish":
            score -= 4 * ema_50_val / 3

        st_val = w.get("supertrend", 4)
        if last.get("st_direction") == "uptrend":
            score += 10 * st_val / 4
        elif last.get("st_direction") == "downtrend":
            score -= 10 * st_val / 4

        adx = last.get("adx", 0)
        adx_val = w.get("adx", 3)
        if adx > 25:
            score += 5 * adx_val / 3 * (1 if last.get("di_signal") == "bullish" else -1)

        bb_val = w.get("bollinger", 3)
        if last.get("bb_signal") == "oversold":
            score += 6 * bb_val / 3
        elif last.get("bb_signal") == "overbought":
            score -= 6 * bb_val / 3

        ichi_val = w.get("ichimoku", 3)
        if last.get("ichimoku_signal") == "bullish":
            score += 8 * ichi_val / 3
        elif last.get("ichimoku_signal") == "bearish":
            score -= 8 * ichi_val / 3

        return score

    def _determine_trend(self, df: pd.DataFrame) -> str:
        if df.empty:
            return "neutral"
        last = df.iloc[-1]
        close = last["close"]
        ema_50 = last.get("ema_50", close)
        ema_200 = last.get("ema_200", close)
        st = last.get("st_direction", "neutral")
        adx = last.get("adx", 0)

        trend_scores = {"bullish": 0, "bearish": 0, "sideways": 0}
        if close > ema_50 > ema_200:
            trend_scores["bullish"] += 2
        elif close < ema_50 < ema_200:
            trend_scores["bearish"] += 2
        else:
            trend_scores["sideways"] += 1

        if st == "uptrend":
            trend_scores["bullish"] += 2
        elif st == "downtrend":
            trend_scores["bearish"] += 2
        else:
            trend_scores["sideways"] += 1

        if adx > 25:
            if last.get("di_signal") == "bullish":
                trend_scores["bullish"] += 1
            elif last.get("di_signal") == "bearish":
                trend_scores["bearish"] += 1

        return max(trend_scores, key=trend_scores.get)

    def _compute_overall_analysis(
        self, timeframes: Dict
    ) -> Dict[str, Any]:
        weights = bot_config["strategy_weights"]
        total_score = 0.0
        trend_counts = {"bullish": 0, "bearish": 0, "sideways": 0}
        primary_tf = bot_config["timeframes"]["primary"]
        primary_weight = 0.4
        confirmation_weight = 0.6
        ml_weight_total = weights.get("ml", 5)

        for tf, data in timeframes.items():
            tf_weight = primary_weight if tf == primary_tf else confirmation_weight / max(len(timeframes) - 1, 1)
            sub_weights = {
                "trend": weights["trend"] / 100 * tf_weight,
                "momentum": weights["momentum"] / 100 * tf_weight,
                "volume": weights["volume"] / 100 * tf_weight,
                "smc": weights["smc"] / 100 * tf_weight,
                "price_action": weights["price_action"] / 100 * tf_weight,
                "ml": ml_weight_total / (100 * len(timeframes)),
            }
            conf_mult = 1.0
            regime = data.get("regime", {})
            if regime.get("trend") in ("strong_uptrend", "strong_downtrend"):
                conf_mult = 1.2
            elif regime.get("trend") == "sideways":
                conf_mult = 0.6
            if regime.get("volatility") == "high":
                conf_mult *= 0.8

            ts = data.get("technical_score", 0) * conf_mult
            ss = data.get("smc_score", 0) * conf_mult
            vs = data.get("volume_score", 0) * conf_mult
            ps = data.get("price_action_score", 0) * conf_mult
            ms = data.get("ml_score", 0)
            trend_dir = data.get("trend", "sideways")
            trend_score = 10 if trend_dir == "bullish" else -10 if trend_dir == "bearish" else 0

            total_score += (
                trend_score * sub_weights["trend"]
                + ts * sub_weights["momentum"]
                + ss * sub_weights["smc"]
                + vs * sub_weights["volume"]
                + ps * sub_weights["price_action"]
                + ms * sub_weights["ml"]
            )

            trend = data.get("trend", "neutral")
            trend_counts[trend] = trend_counts.get(trend, 0) + 1

        max_trend = max(trend_counts, key=trend_counts.get)
        return {
            "total_score": total_score,
            "trend": max_trend,
            "trend_alignment": trend_counts,
            "timeframe_count": len(timeframes),
        }

    async def analyze_market(self) -> List[Dict]:
        sentiment = await self.sentiment.compute_all()
        return {"sentiment": sentiment}

    async def close(self):
        await self.sentiment.close()
