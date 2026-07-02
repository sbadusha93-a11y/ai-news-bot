from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from loguru import logger


class MarketAnalyzer:
    def __init__(self):
        pass

    def rank_coins(self, analyses: Dict[str, Dict]) -> List[Dict]:
        ranked = []
        for symbol, analysis in analyses.items():
            signals = analysis.get("signals", {})
            overall = analysis.get("overall", {})

            rank_score = 0.0
            if signals.get("direction") in ("long", "short"):
                confidence = signals.get("confidence", 0)
                trade_quality = signals.get("trade_quality", 0)

                vol_score = 0
                timeframes = analysis.get("timeframes", {})
                for tf_data in timeframes.values():
                    last = tf_data.get("last_row", {})
                    vol = last.get("volume", 0)
                    if vol > 0:
                        vol_score += min(np.log10(vol) * 10, 50)

                rank_score = confidence * 0.4 + trade_quality * 0.3 + \
                             (100 - signals.get("risk_score", 50)) * 0.3

            ranked.append({
                "symbol": symbol,
                "rank_score": rank_score,
                "direction": signals.get("direction", "neutral"),
                "confidence": signals.get("confidence", 0),
                "trade_quality": signals.get("trade_quality", 0),
                "risk_score": signals.get("risk_score", 100),
                "analysis": analysis,
            })

        ranked.sort(key=lambda x: x["rank_score"], reverse=True)
        return ranked

    def filter_tradeable(self, ranked: List[Dict]) -> List[Dict]:
        tradeable = []
        for item in ranked:
            if item["direction"] in ("long", "short") and \
               item["confidence"] >= 90 and \
               item["risk_score"] <= 50:
                tradeable.append(item)
        return tradeable

    def select_top_opportunities(
        self, ranked: List[Dict], top_n: int = 10
    ) -> List[Dict]:
        filtered = self.filter_tradeable(ranked)
        return filtered[:top_n]
