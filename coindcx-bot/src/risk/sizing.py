import math
from typing import Dict, Optional, Tuple

import numpy as np
from loguru import logger

from src.config import bot_config, settings


class PositionSizer:
    def __init__(self, balance: Optional[float] = None):
        self.balance = balance if balance is not None else settings.initial_balance
        self.config = bot_config["risk"]
        self.max_risk_per_trade = self.config["max_risk_per_trade"] / 100
        self._trade_history: list = []

    def update_trade_history(self, trades: list):
        self._trade_history = trades

    def calculate_position_size(
        self,
        price: float,
        stop_loss: float,
        risk_percent: Optional[float] = None,
        leverage: int = 1,
        confidence: float = 85.0,
        volatility_mult: float = 1.0,
    ) -> Dict:
        if risk_percent is None:
            risk_percent = self.max_risk_per_trade

        kelly_fraction = self._get_kelly_fraction(confidence)
        if kelly_fraction > 0:
            risk_percent = min(risk_percent, kelly_fraction)

        vol_adjusted = self._volatility_adjustment(volatility_mult)
        risk_percent *= vol_adjusted

        risk_amount = self.balance * risk_percent
        price_risk = abs(price - stop_loss)
        if price_risk <= 0:
            return {"error": "Invalid stop loss"}

        position_size = risk_amount / price_risk
        position_value = position_size * price

        max_pct = self.config.get("portfolio", {}).get("max_concentration_single", 0.25)
        max_position_value = self.balance * max_pct
        position_value = min(position_value, max_position_value)
        position_size = position_value / price

        return {
            "position_size": round(position_size, 6),
            "position_value": round(position_value, 2),
            "risk_amount": round(risk_amount, 2),
            "risk_percent": round(risk_percent * 100, 2),
            "leverage": leverage,
            "kelly_fraction": round(kelly_fraction, 4),
        }

    def _get_kelly_fraction(self, confidence: float) -> float:
        kelly_cfg = self.config.get("kelly", {})
        if not kelly_cfg.get("enabled", True):
            return 0.0

        recent = [t for t in self._trade_history[-50:]]
        if len(recent) < 10:
            return 0.0

        wins = [t for t in recent if t.get("pnl", 0) > 0]
        losses = [t for t in recent if t.get("pnl", 0) <= 0]
        win_rate = len(wins) / len(recent) if recent else 0.5
        avg_win = np.mean([t["pnl"] for t in wins]) if wins else 0
        avg_loss = abs(np.mean([t["pnl"] for t in losses])) if losses else 1

        if avg_loss == 0:
            return 0.0

        b = abs(avg_win) / avg_loss if avg_loss > 0 else 1
        kelly = (win_rate * b - (1 - win_rate)) / b if b > 0 else 0
        kelly = max(0, kelly)

        edge_mult = kelly_cfg.get("edge_multiplier", 0.25)
        max_frac = kelly_cfg.get("max_fraction", 0.02)
        return min(kelly * edge_mult, max_frac)

    def _volatility_adjustment(self, volatility_mult: float) -> float:
        if volatility_mult >= 1.5:
            return 0.6
        if volatility_mult >= 1.2:
            return 0.8
        if volatility_mult <= 0.5:
            return 1.3
        if volatility_mult <= 0.7:
            return 1.15
        return 1.0

    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: float,
        direction: str,
        atr_multiplier: Optional[float] = None,
        volatility_mult: float = 1.0,
    ) -> float:
        if atr_multiplier is None:
            atr_multiplier = self.config["stop_loss_atr_multiplier"]

        adj_multiplier = atr_multiplier
        if volatility_mult > 1.2:
            adj_multiplier = atr_multiplier * 1.2
        elif volatility_mult < 0.7:
            adj_multiplier = atr_multiplier * 0.85

        atr_distance = atr * adj_multiplier
        if direction == "long":
            return entry_price - atr_distance
        else:
            return entry_price + atr_distance

    def calculate_take_profits(
        self,
        entry_price: float,
        stop_loss: float,
        direction: str,
    ) -> Dict[int, float]:
        risk = abs(entry_price - stop_loss)
        levels = self.config["take_profit_levels"]
        take_profits = {}

        for level in levels:
            reward = risk * level["ratio"]
            if direction == "long":
                tp_price = entry_price + reward
            else:
                tp_price = entry_price - reward
            take_profits[level["level"]] = round(tp_price, 8)

        return take_profits

    def calculate_trailing_stop(
        self,
        current_price: float,
        entry_price: float,
        atr: float,
        direction: str,
        highest_price: Optional[float] = None,
        lowest_price: Optional[float] = None,
        volatility_mult: float = 1.0,
    ) -> Tuple[float, bool]:
        activation_distance = self.config["trailing_stop_activation"]
        trail_distance = self.config["trailing_stop_distance"]

        adj_activation = activation_distance
        adj_trail = trail_distance
        if volatility_mult > 1.2:
            adj_activation *= 1.3
            adj_trail *= 1.3
        elif volatility_mult < 0.7:
            adj_activation *= 0.8
            adj_trail *= 0.8

        if direction == "long":
            if highest_price is None:
                highest_price = current_price
            activation_price = entry_price * (1 + adj_activation / 100)
            if current_price >= activation_price:
                trail_price = highest_price * (1 - adj_trail / 100)
                return trail_price, True
            return entry_price * (1 - adj_trail / 100), False
        else:
            if lowest_price is None:
                lowest_price = current_price
            activation_price = entry_price * (1 - adj_activation / 100)
            if current_price <= activation_price:
                trail_price = lowest_price * (1 + adj_trail / 100)
                return trail_price, True
            return entry_price * (1 + adj_trail / 100), False

    def calculate_break_even_stop(
        self,
        current_price: float,
        entry_price: float,
        direction: str,
        volatility_mult: float = 1.0,
    ) -> Tuple[float, bool]:
        trigger_multiple = self.config["break_even_trigger"]
        adj_trigger = trigger_multiple
        if volatility_mult > 1.2:
            adj_trigger *= 1.3
        elif volatility_mult < 0.7:
            adj_trigger *= 0.8

        buffer = 0.001
        if volatility_mult > 1.5:
            buffer = 0.003
        elif volatility_mult > 1.2:
            buffer = 0.002

        if direction == "long":
            target = entry_price * (1 + adj_trigger / 100)
            if current_price >= target:
                return entry_price * (1 + buffer), True
        else:
            target = entry_price * (1 - adj_trigger / 100)
            if current_price <= target:
                return entry_price * (1 - buffer), True
        return 0.0, False

    def update_balance(self, new_balance: float):
        self.balance = new_balance
