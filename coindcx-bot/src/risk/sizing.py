import math
from typing import Dict, Optional, Tuple

import numpy as np
from loguru import logger

from src.config import bot_config


class PositionSizer:
    def __init__(self, balance: float = 10000.0):
        self.balance = balance
        self.config = bot_config["risk"]
        self.max_risk_per_trade = self.config["max_risk_per_trade"] / 100

    def calculate_position_size(
        self,
        price: float,
        stop_loss: float,
        risk_percent: Optional[float] = None,
        leverage: int = 1,
    ) -> Dict:
        if risk_percent is None:
            risk_percent = self.max_risk_per_trade

        risk_amount = self.balance * risk_percent
        if leverage > 1:
            risk_amount *= leverage

        price_risk = abs(price - stop_loss)
        if price_risk == 0:
            return {"error": "Invalid stop loss"}

        position_size = risk_amount / price_risk
        position_value = position_size * price

        max_position_value = self.balance * leverage * 0.25
        position_value = min(position_value, max_position_value)
        position_size = position_value / price

        return {
            "position_size": round(position_size, 6),
            "position_value": round(position_value, 2),
            "risk_amount": round(risk_amount, 2),
            "risk_percent": round(risk_percent * 100, 2),
            "leverage": leverage,
        }

    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: float,
        direction: str,
        atr_multiplier: Optional[float] = None,
    ) -> float:
        if atr_multiplier is None:
            atr_multiplier = self.config["stop_loss_atr_multiplier"]

        atr_distance = atr * atr_multiplier
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
    ) -> Tuple[float, bool]:
        activation_distance = self.config["trailing_stop_activation"]
        trail_distance = self.config["trailing_stop_distance"]

        if direction == "long":
            if highest_price is None:
                highest_price = current_price
            activation_price = entry_price * (1 + activation_distance / 100)
            if current_price >= activation_price:
                trail_price = highest_price * (1 - trail_distance / 100)
                return trail_price, True
        else:
            if lowest_price is None:
                lowest_price = current_price
            activation_price = entry_price * (1 - activation_distance / 100)
            if current_price <= activation_price:
                trail_price = lowest_price * (1 + trail_distance / 100)
                return trail_price, True

        return stop_loss, False

    def calculate_break_even_stop(
        self,
        current_price: float,
        entry_price: float,
        direction: str,
    ) -> Tuple[float, bool]:
        trigger_multiple = self.config["break_even_trigger"]
        if direction == "long":
            target = entry_price * (1 + trigger_multiple / 100)
            if current_price >= target:
                return entry_price * 1.001, True
        else:
            target = entry_price * (1 - trigger_multiple / 100)
            if current_price <= target:
                return entry_price * 0.999, True
        return 0.0, False

    def update_balance(self, new_balance: float):
        self.balance = new_balance
