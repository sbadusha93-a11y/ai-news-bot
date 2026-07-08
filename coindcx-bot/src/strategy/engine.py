import asyncio
from typing import Any, Dict, List, Optional, Tuple

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
        self.timeframes = (
            [bot_config["timeframes"]["primary"]]
            + bot_config["timeframes"]["confirmation"]
        )

    async def analyze_symbol(
        self, symbol: str, df_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        analysis = {
            "symbol": symbol,
            "timeframes": {},
            "overall": {},
            "signals": {},
        }

        for tf, df in df_dict.items():
            df = self.technical.compute_all(df)
            df = self.smc.compute_all(df)
            df = self.volume.compute_all(df)
            df = self.price_action.compute_all(df)

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
            analysis["timeframes"][tf] = {
                "last_row": last.to_dict() if not last.empty else {},
                "technical_score": self._compute_technical_score(df),
                "smc_score": self.smc.get_smc_score(df),
                "volume_score": self.volume.get_volume_score(df),
                "price_action_score": self.price_action.get_price_action_score(df),
                "ml_score": ml_score,
                "ml_confidence": ml_confidence,
                "trend": self._determine_trend(df),
                "support": last.get("support", 0),
                "resistance": last.get("resistance", 0),
            }

        analysis["overall"] = self._compute_overall_analysis(analysis["timeframes"])
        analysis["signals"] = self.scorer.compute_signals(analysis)
        return analysis

    def _compute_technical_score(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0

        last = df.iloc[-1]
        score = 0.0

        if last.get("rsi", 50) < 30:
            score += 8
        elif last.get("rsi", 50) > 70:
            score -= 8

        if last.get("macd_signal_line") == "bullish":
            score += 10
        elif last.get("macd_signal_line") == "bearish":
            score -= 10

        if last.get("macd_histogram_signal") == "increasing":
            score += 5
        else:
            score -= 5

        if last.get("ema_9_20_cross") == "bullish":
            score += 6
        elif last.get("ema_9_20_cross") == "bearish":
            score -= 6

        if last.get("ema_20_50_cross") == "bullish":
            score += 6
        elif last.get("ema_20_50_cross") == "bearish":
            score -= 6

        if last.get("ema_50_100_cross") == "bullish":
            score += 4
        elif last.get("ema_50_100_cross") == "bearish":
            score -= 4

        if last.get("st_direction") == "uptrend":
            score += 10
        elif last.get("st_direction") == "downtrend":
            score -= 10

        if last.get("adx", 0) > 25:
            score += 5 * (1 if last.get("di_signal") == "bullish" else -1)

        if last.get("bb_signal") == "oversold":
            score += 6
        elif last.get("bb_signal") == "overbought":
            score -= 6

        if last.get("ichimoku_signal") == "bullish":
            score += 8
        elif last.get("ichimoku_signal") == "bearish":
            score -= 8

        return score

    def _determine_trend(self, df: pd.DataFrame) -> str:
        if df.empty:
            return "neutral"

        last = df.iloc[-1]
        ema_50 = last.get("ema_50", last["close"])
        ema_200 = last.get("ema_200", last["close"])

        if last["close"] > ema_50 > ema_200:
            return "bullish"
        elif last["close"] < ema_50 < ema_200:
            return "bearish"
        else:
            return "sideways"

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

            ts = data.get("technical_score", 0)
            ss = data.get("smc_score", 0)
            vs = data.get("volume_score", 0)
            ps = data.get("price_action_score", 0)
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
