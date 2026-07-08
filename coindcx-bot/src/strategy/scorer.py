import numpy as np
from typing import Any, Dict, List, Optional

from src.config import bot_config


class TradeScorer:
    def __init__(self):
        self.min_confidence = bot_config["bot"]["min_confidence"]
        self.weights = bot_config["strategy_weights"]

    def compute_signals(self, analysis: Dict) -> Dict[str, Any]:
        timeframes = analysis.get("timeframes", {})
        overall = analysis.get("overall", {})

        buy_score = 0.0
        sell_score = 0.0
        total_indicators = 0
        max_possible = 100.0

        for tf, data in timeframes.items():
            ts = data.get("technical_score", 0)
            ss = data.get("smc_score", 0)
            vs = data.get("volume_score", 0)
            ps = data.get("price_action_score", 0)

            w = self.weights
            total_w = w["trend"] + w["momentum"] + w["volume"] + w["smc"] + w["price_action"]
            tech_w = (w["trend"] + w["momentum"]) / total_w if total_w > 0 else 0.4
            smc_w = w["smc"] / total_w if total_w > 0 else 0.3
            vol_w = w["volume"] / total_w if total_w > 0 else 0.2
            pa_w = w["price_action"] / total_w if total_w > 0 else 0.1

            if ts > 0:
                buy_score += ts * tech_w
            else:
                sell_score += abs(ts) * tech_w

            if ss > 0:
                buy_score += ss * smc_w
            else:
                sell_score += abs(ss) * smc_w

            if vs > 0:
                buy_score += vs * vol_w
            else:
                sell_score += abs(vs) * vol_w

            if ps > 0:
                buy_score += ps * pa_w
            else:
                sell_score += abs(ps) * pa_w

            total_indicators += 1

        if total_indicators > 0:
            buy_score /= total_indicators
            sell_score /= total_indicators

        total_score = buy_score + sell_score
        buy_probability = (buy_score / max(total_score, 1)) * 100 if total_score > 0 else 50
        sell_probability = (sell_score / max(total_score, 1)) * 100 if total_score > 0 else 50

        confidence = max(buy_probability, sell_probability)
        trade_quality = self._compute_trade_quality(buy_score, sell_score, analysis)
        risk_score = self._compute_risk_score(buy_score, sell_score, analysis)

        direction = "long" if buy_probability > sell_probability else "short" if sell_probability > buy_probability else "neutral"

        return {
            "direction": direction,
            "buy_probability": round(buy_probability, 2),
            "sell_probability": round(sell_probability, 2),
            "confidence": round(confidence, 2),
            "trade_quality": round(trade_quality, 2),
            "risk_score": round(risk_score, 2),
            "is_tradeable": confidence >= self.min_confidence,
            "reason": self._generate_reason(analysis, direction, buy_probability, sell_probability),
        }

    def _compute_trade_quality(
        self, buy_score: float, sell_score: float, analysis: Dict
    ) -> float:
        overall = analysis.get("overall", {})
        total_score = abs(overall.get("total_score", 0))
        trend_alignment = overall.get("trend_alignment", {})
        alignment_score = max(trend_alignment.values()) / max(len(trend_alignment), 1) * 100 if trend_alignment else 50

        quality = (min(abs(total_score) * 2, 50) + alignment_score * 0.5)
        return min(quality, 100)

    def _compute_risk_score(
        self, buy_score: float, sell_score: float, analysis: Dict
    ) -> float:
        rs = 30.0
        timeframes = analysis.get("timeframes", {})

        for tf, data in timeframes.items():
            last = data.get("last_row", {})
            atr_percent = last.get("atr_percent", 0)
            if atr_percent > 5:
                rs += 10
            elif atr_percent > 3:
                rs += 5

            adx = last.get("adx", 0)
            if adx > 40:
                rs -= 5
            elif adx < 15:
                rs += 10

            volume_spike = last.get("volume_spike", False)
            if volume_spike:
                rs += 5

            doji = last.get("doji", False)
            if doji:
                rs += 3

        return min(max(rs, 0), 100)

    def _generate_reason(
        self,
        analysis: Dict,
        direction: str,
        buy_prob: float,
        sell_prob: float,
    ) -> str:
        reasons = []
        timeframes = analysis.get("timeframes", {})

        for tf, data in timeframes.items():
            last = data.get("last_row", {})
            trend = data.get("trend", "neutral")

            if direction == "long":
                if last.get("st_direction") == "uptrend":
                    reasons.append(f"SuperTrend uptrend on {tf}")
                if last.get("macd_signal_line") == "bullish":
                    reasons.append(f"MACD bullish on {tf}")
                if last.get("ema_9_20_cross") == "bullish":
                    reasons.append(f"EMA 9/20 bullish cross on {tf}")
                if last.get("rsi", 50) < 30:
                    reasons.append(f"RSI oversold on {tf}")
                if last.get("bos") == "bullish_bos":
                    reasons.append(f"BOS bullish on {tf}")
                if last.get("bullish_engulfing"):
                    reasons.append(f"Bullish engulfing on {tf}")
                if last.get("volume_divergence") == "bullish_divergence":
                    reasons.append(f"Volume divergence bullish on {tf}")

            else:
                if last.get("st_direction") == "downtrend":
                    reasons.append(f"SuperTrend downtrend on {tf}")
                if last.get("macd_signal_line") == "bearish":
                    reasons.append(f"MACD bearish on {tf}")
                if last.get("ema_9_20_cross") == "bearish":
                    reasons.append(f"EMA 9/20 bearish cross on {tf}")
                if last.get("rsi", 50) > 70:
                    reasons.append(f"RSI overbought on {tf}")
                if last.get("bos") == "bearish_bos":
                    reasons.append(f"BOS bearish on {tf}")
                if last.get("bearish_engulfing"):
                    reasons.append(f"Bearish engulfing on {tf}")
                if last.get("volume_divergence") == "bearish_divergence":
                    reasons.append(f"Volume divergence bearish on {tf}")

        sentiment = analysis.get("sentiment", {})
        overall_sentiment = sentiment.get("overall_sentiment", {}).get("classification", "neutral")
        if overall_sentiment == "bullish" and direction == "long":
            reasons.append(f"Market sentiment bullish")
        elif overall_sentiment == "bearish" and direction == "short":
            reasons.append(f"Market sentiment bearish")

        return "; ".join(reasons[:5]) if reasons else "No clear signal"
