import math
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from loguru import logger


class PortfolioRiskManager:
    def __init__(self, max_leverage: float = 5.0):
        self.max_leverage = max_leverage
        self._correlation_matrix: Optional[pd.DataFrame] = None
        self._last_correlation_update = 0

    def compute_correlation_matrix(
        self, price_data: Dict[str, pd.Series]
    ) -> pd.DataFrame:
        df = pd.DataFrame(price_data)
        self._correlation_matrix = df.corr(method="spearman")
        return self._correlation_matrix

    def check_correlation_risk(
        self,
        positions: Dict[str, Dict],
        correlation_threshold: float = 0.70,
        max_correlated_exposure: float = 0.40,
    ) -> Dict[str, Any]:
        if not positions or self._correlation_matrix is None:
            return {"is_safe": True, "violations": []}

        symbols = list(positions.keys())
        violations = []

        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                s1, s2 = symbols[i], symbols[j]
                if s1 not in self._correlation_matrix.index or s2 not in self._correlation_matrix.columns:
                    continue
                corr = self._correlation_matrix.loc[s1, s2]
                if abs(corr) >= correlation_threshold:
                    p1_side = positions[s1].get("side", "long")
                    p2_side = positions[s2].get("side", "long")
                    if p1_side == p2_side:
                        violations.append({
                            "symbols": [s1, s2],
                            "correlation": round(float(corr), 3),
                            "risk": "high_correlation_same_direction",
                            "action": "reduce_exposure",
                        })

        same_side_positions = {}
        total_notional = 0.0
        for sym, pos in positions.items():
            side = pos.get("side", "long")
            val = pos.get("quantity", 0) * pos.get("entry_price", 0)
            total_notional += val
            if side not in same_side_positions:
                same_side_positions[side] = {"symbols": [], "total_notional": 0.0}
            same_side_positions[side]["symbols"].append(sym)
            same_side_positions[side]["total_notional"] += val

        for side, data in same_side_positions.items():
            if data["total_notional"] / max(total_notional, 1) > max_correlated_exposure:
                violations.append({
                    "side": side,
                    "exposure_pct": round(data["total_notional"] / max(total_notional, 1) * 100, 1),
                    "risk": "concentration_exceeded",
                    "action": "reduce_exposure",
                })

        is_safe = len(violations) == 0
        return {
            "is_safe": is_safe,
            "violations": violations,
            "total_notional": round(total_notional, 2),
        }

    def calculate_portfolio_var(
        self,
        positions: Dict[str, Dict],
        confidence: float = 0.95,
    ) -> float:
        if not positions or self._correlation_matrix is None:
            return 0.0

        weights = []
        variances = []
        symbols = []
        total_val = 0.0

        for sym, pos in positions.items():
            val = pos.get("quantity", 0) * pos.get("entry_price", 0)
            total_val += val
            symbols.append(sym)

        if total_val == 0:
            return 0.0

        for sym in symbols:
            pos = positions[sym]
            weight = (pos["quantity"] * pos["entry_price"]) / total_val
            weights.append(weight)
            daily_vol = 0.02
            variances.append(daily_vol ** 2)

        weights_arr = np.array(weights)
        cov_matrix = np.diag(variances)
        if self._correlation_matrix is not None:
            corr = self._correlation_matrix.reindex(
                index=symbols, columns=symbols, fill_value=0
            ).values
            vol_arr = np.sqrt(variances)
            cov_matrix = np.outer(vol_arr, vol_arr) * corr

        portfolio_variance = weights_arr.T @ cov_matrix @ weights_arr
        portfolio_std = np.sqrt(portfolio_variance)

        z_score = {0.95: 1.645, 0.99: 2.326}.get(confidence, 1.645)
        var_pct = z_score * portfolio_std
        var_dollar = var_pct * total_val

        return float(var_dollar)

    def compute_liquidation_price(
        self,
        entry_price: float,
        quantity: float,
        direction: str,
        leverage: float,
        maintenance_margin_rate: float = 0.005,
    ) -> float:
        notional = entry_price * quantity
        position_margin = notional / leverage
        maintenance_margin = notional * maintenance_margin_rate

        if direction == "long":
            liq_price = (notional - position_margin + maintenance_margin) / quantity
        else:
            liq_price = (notional + position_margin - maintenance_margin) / quantity

        return round(liq_price, 8)

    def check_liquidation_safety(
        self,
        entry_price: float,
        stop_loss: float,
        quantity: float,
        direction: str,
        leverage: float,
        safety_margin: float = 0.3,
    ) -> Dict[str, Any]:
        liq_price = self.compute_liquidation_price(
            entry_price, quantity, direction, leverage
        )
        sl_distance = abs(entry_price - stop_loss)
        liq_distance = abs(entry_price - liq_price)

        if liq_distance == 0:
            return {"is_safe": False, "liq_price": liq_price, "safety_ratio": 0}

        safety_ratio = sl_distance / liq_distance
        is_safe = safety_ratio <= safety_margin

        return {
            "is_safe": is_safe,
            "liq_price": liq_price,
            "safety_ratio": round(safety_ratio, 3),
            "stop_loss_distance": round(sl_distance, 4),
            "liq_distance": round(liq_distance, 4),
        }

    def calculate_weighted_kelly_fraction(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        edge_multiplier: float = 0.25,
        max_fraction: float = 0.02,
    ) -> float:
        if avg_loss == 0:
            return max_fraction
        win_prob = win_rate / 100.0
        loss_prob = 1 - win_prob
        b = avg_win / abs(avg_loss) if avg_loss != 0 else 1
        kelly = (win_prob * b - loss_prob) / b if b != 0 else 0
        fraction = max(0, kelly * edge_multiplier)
        return min(fraction, max_fraction)
