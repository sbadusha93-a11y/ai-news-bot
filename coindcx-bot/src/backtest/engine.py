from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from loguru import logger

from src.config import bot_config
from src.indicators.technical import TechnicalIndicators
from src.indicators.smc import SMCIndicators
from src.indicators.volume import VolumeIndicators
from src.indicators.price_action import PriceActionIndicators
from src.risk.manager import RiskManager
from src.risk.sizing import PositionSizer
from src.strategy.engine import StrategyEngine


class BacktestEngine:
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.risk_manager = RiskManager()
        self.position_sizer = PositionSizer(initial_balance)
        self.technical = TechnicalIndicators()
        self.smc = SMCIndicators()
        self.volume = VolumeIndicators()
        self.price_action = PriceActionIndicators()
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = [initial_balance]
        self._current_day = None
        self._current_week = None

    async def run(
        self,
        df: pd.DataFrame,
        symbol: str = "BACKTEST",
        commission: float = 0.001,
    ) -> Dict[str, Any]:
        if df.empty or len(df) < 100:
            return {"error": "Insufficient data"}

        df = df.copy()
        df = self.technical.compute_all(df)
        df = self.smc.compute_all(df)
        df = self.volume.compute_all(df)
        df = self.price_action.compute_all(df)

        position = None
        balance = self.initial_balance
        self.trades = []
        self.equity_curve = [balance]

        for i in range(200, len(df)):
            row = df.iloc[:i + 1]
            current = df.iloc[i]
            price = current["close"]

            candle_day = df.index[i].date()
            candle_week = df.index[i].isocalendar()[1]
            if self._current_day is not None and candle_day != self._current_day:
                self._current_day = candle_day
                self.risk_manager.reset_daily()
                self.risk_manager.consecutive_losses = 0
                self.risk_manager.is_paused = False
            elif self._current_day is None:
                self._current_day = candle_day
                self._current_week = candle_week
            if self._current_week is not None and candle_week != self._current_week:
                self._current_week = candle_week
                self.risk_manager.reset_weekly()
            if self.risk_manager.is_paused:
                self.risk_manager.is_paused = False

            if position:
                sl = position["stop_loss"]
                tp1 = position.get("take_profit_1", 0)
                direction = position["side"]
                entry = position["entry_price"]

                tp2 = position.get("take_profit_2", 0)
                tp3 = position.get("take_profit_3", 0)
                exit_reason = None
                exit_price = None

                if direction == "long":
                    if price <= sl:
                        exit_reason = "stop_loss"
                        exit_price = sl
                    elif tp3 > 0 and price >= tp3:
                        exit_reason = "take_profit_3"
                        exit_price = tp3
                    elif tp2 > 0 and price >= tp2:
                        exit_reason = "take_profit_2"
                        exit_price = tp2
                    elif tp1 > 0 and price >= tp1:
                        exit_reason = "take_profit_1"
                        exit_price = tp1
                else:
                    if price >= sl:
                        exit_reason = "stop_loss"
                        exit_price = sl
                    elif tp3 > 0 and price <= tp3:
                        exit_reason = "take_profit_3"
                        exit_price = tp3
                    elif tp2 > 0 and price <= tp2:
                        exit_reason = "take_profit_2"
                        exit_price = tp2
                    elif tp1 > 0 and price <= tp1:
                        exit_reason = "take_profit_1"
                        exit_price = tp1

                if exit_reason:
                    pnl = (exit_price - entry) * position["quantity"] if direction == "long" \
                          else (entry - exit_price) * position["quantity"]
                    pnl_percent = (pnl / (entry * position["quantity"])) * 100

                    balance += pnl
                    position["exit_price"] = exit_price
                    position["pnl"] = pnl
                    position["pnl_percent"] = pnl_percent
                    position["reason_exit"] = exit_reason
                    position["exit_time"] = df.index[i]
                    self.trades.append(position)
                    self.equity_curve.append(balance)

                    self.risk_manager.record_trade(position)

                    if self.risk_manager.consecutive_losses >= \
                       self.risk_manager.config["max_consecutive_losses"]:
                        self.risk_manager.pause_trading(60)
                        position = None
                        continue

                    position = None
                    self.position_sizer.update_balance(balance)
                    continue

            if not position and self.risk_manager.can_trade():
                last_rows = df.iloc[max(0, i - 50):i + 1]
                min_rr = bot_config["bot"]["min_rr"]
                if self._is_bullish_signal(last_rows):
                    atr = current.get("atr", 0)
                    sl = self.position_sizer.calculate_stop_loss(price, atr, "long")
                    tps = self.position_sizer.calculate_take_profits(price, sl, "long")
                    pos_size = self.position_sizer.calculate_position_size(price, sl)

                    if "error" not in pos_size:
                        rr = abs(tps.get(1, price) - price) / abs(price - sl)
                        if rr >= min_rr:
                            cost = price * pos_size["position_size"]
                            if cost <= balance:
                                position = {
                                    "symbol": symbol,
                                    "side": "long",
                                    "entry_price": price,
                                    "quantity": pos_size["position_size"],
                                    "stop_loss": sl,
                                    "take_profit_1": tps.get(1, 0),
                                    "take_profit_2": tps.get(2, 0),
                                    "take_profit_3": tps.get(3, 0),
                                    "entry_time": df.index[i],
                                    "status": "open",
                                }
                elif self._is_bearish_signal(last_rows):
                    atr = current.get("atr", 0)
                    sl = self.position_sizer.calculate_stop_loss(price, atr, "short")
                    tps = self.position_sizer.calculate_take_profits(price, sl, "short")
                    pos_size = self.position_sizer.calculate_position_size(price, sl)

                    if "error" not in pos_size:
                        rr = abs(price - tps.get(1, price)) / abs(price - sl)
                        if rr >= min_rr:
                            cost = price * pos_size["position_size"]
                            if cost <= balance:
                                position = {
                                    "symbol": symbol,
                                    "side": "short",
                                    "entry_price": price,
                                    "quantity": pos_size["position_size"],
                                    "stop_loss": sl,
                                    "take_profit_1": tps.get(1, 0),
                                    "take_profit_2": tps.get(2, 0),
                                    "take_profit_3": tps.get(3, 0),
                                    "entry_time": df.index[i],
                                    "status": "open",
                                }

        if position:
            current = df.iloc[-1]
            pnl = (current["close"] - position["entry_price"]) * position["quantity"]
            pnl_percent = (pnl / (position["entry_price"] * position["quantity"])) * 100
            position["exit_price"] = current["close"]
            position["pnl"] = pnl
            position["pnl_percent"] = pnl_percent
            position["reason_exit"] = "end_of_backtest"
            balance += pnl
            self.trades.append(position)
            self.equity_curve.append(balance)

        self.balance = balance
        return self._compute_metrics()

    def _is_bullish_signal(self, df: pd.DataFrame) -> bool:
        last = df.iloc[-1]
        score = 0

        if last.get("st_direction") == "uptrend":
            score += 1
        if last.get("macd_signal_line") == "bullish":
            score += 1
        if last.get("rsi", 50) > 50:
            score += 1
        if last.get("ema_9_20_cross") == "bullish":
            score += 1
        if last.get("bos") == "bullish_bos":
            score += 1
        if last.get("volume_spike"):
            score += 1

        return score >= 4

    def _is_bearish_signal(self, df: pd.DataFrame) -> bool:
        last = df.iloc[-1]
        score = 0

        if last.get("st_direction") == "downtrend":
            score += 1
        if last.get("macd_signal_line") == "bearish":
            score += 1
        if last.get("rsi", 50) < 50:
            score += 1
        if last.get("ema_9_20_cross") == "bearish":
            score += 1
        if last.get("bos") == "bearish_bos":
            score += 1
        if last.get("volume_spike"):
            score += 1

        return score >= 4

    def _compute_metrics(self) -> Dict[str, Any]:
        total = len(self.trades)
        if total == 0:
            return {"total_trades": 0, "net_profit": 0}

        wins = [t for t in self.trades if t.get("pnl", 0) > 0]
        losses = [t for t in self.trades if t.get("pnl", 0) <= 0]
        win_rate = len(wins) / total * 100 if total > 0 else 0

        gross_profit = sum(t["pnl"] for t in wins)
        gross_loss = abs(sum(t["pnl"] for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        net_profit = self.balance - self.initial_balance
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(365) if len(returns) > 1 and np.std(returns) > 0 else 0

        cum_max = np.maximum.accumulate(self.equity_curve)
        drawdowns = (cum_max - self.equity_curve) / cum_max * 100
        max_dd = np.max(drawdowns) if len(drawdowns) > 0 else 0

        avg_trade = net_profit / total
        avg_win = np.mean([t["pnl"] for t in wins]) if wins else 0
        avg_loss = np.mean([t["pnl"] for t in losses]) if losses else 0

        positive_returns = [r for r in returns if r > 0]
        negative_returns = [r for r in returns if r < 0]
        sortino = np.mean(returns) / np.std(negative_returns) * np.sqrt(365) if negative_returns and np.std(negative_returns) > 0 else 0

        expectancy = (win_rate / 100 * avg_win) - ((1 - win_rate / 100) * abs(avg_loss))
        recovery_factor = abs(net_profit / max_dd) if max_dd > 0 else 0

        return {
            "total_trades": total,
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
            "net_profit": round(net_profit, 2),
            "total_return": round(net_profit / self.initial_balance * 100, 2),
            "max_drawdown": round(max_dd, 2),
            "sharpe_ratio": round(sharpe, 4),
            "sortino_ratio": round(sortino, 4),
            "average_trade": round(avg_trade, 2),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "expectancy": round(expectancy, 4),
            "recovery_factor": round(recovery_factor, 2),
            "final_balance": round(self.balance, 2),
        }
