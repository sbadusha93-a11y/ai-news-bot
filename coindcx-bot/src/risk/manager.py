from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import numpy as np
from loguru import logger

from src.config import bot_config


class RiskManager:
    def __init__(self):
        self.config = bot_config["risk"]
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.monthly_pnl = 0.0
        self.consecutive_losses = 0
        self.total_pnl = 0.0
        self.peak_balance = 10000.0
        self.max_drawdown = 0.0
        self.daily_trades = []
        self.weekly_trades = []
        self.is_paused = False
        self.pause_until: Optional[datetime] = None
        self.trade_history: List[Dict] = []

    def can_trade(self) -> bool:
        if self.is_paused:
            if self.pause_until and datetime.now(timezone.utc) >= self.pause_until:
                self.is_paused = False
                self.pause_until = None
                logger.info("Trading resumed after pause")
                return True
            return False

        if self.consecutive_losses >= self.config["max_consecutive_losses"]:
            logger.warning(f"Max consecutive losses ({self.consecutive_losses}) reached")
            if self.config["auto_pause_after_losses"]:
                self.pause_trading()
            return False

        if abs(self.daily_pnl) >= self.config["max_daily_risk"]:
            logger.warning(f"Daily risk limit reached: {self.daily_pnl}")
            return False

        if abs(self.weekly_pnl) >= self.config["max_weekly_risk"]:
            logger.warning(f"Weekly risk limit reached: {self.weekly_pnl}")
            return False

        if self.max_drawdown >= self.config["max_drawdown"]:
            logger.warning(f"Max drawdown reached: {self.max_drawdown}%")
            return False

        return True

    def pause_trading(self, duration_minutes: Optional[int] = None):
        if duration_minutes is None:
            duration_minutes = self.config["pause_duration_minutes"]
        self.is_paused = True
        self.pause_until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        logger.warning(f"Trading paused for {duration_minutes} minutes until {self.pause_until}")

    def resume_trading(self):
        self.is_paused = False
        self.pause_until = None
        self.consecutive_losses = 0
        logger.info("Trading resumed manually")

    def record_trade(self, trade_result: Dict):
        self.trade_history.append(trade_result)
        pnl = trade_result.get("pnl", 0)
        self.total_pnl += pnl
        self.daily_pnl += pnl
        self.weekly_pnl += pnl
        self.monthly_pnl += pnl

        self.daily_trades.append(trade_result)
        self.weekly_trades.append(trade_result)

        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        current_balance = 10000 + self.total_pnl
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        dd = (self.peak_balance - current_balance) / self.peak_balance * 100
        self.max_drawdown = max(self.max_drawdown, dd)

    def reset_daily(self):
        self.daily_pnl = 0.0
        self.daily_trades = []

    def reset_weekly(self):
        self.weekly_pnl = 0.0
        self.weekly_trades = []

    def reset_monthly(self):
        self.monthly_pnl = 0.0

    def get_metrics(self) -> Dict:
        total = len(self.trade_history)
        wins = sum(1 for t in self.trade_history if t.get("pnl", 0) > 0)
        losses = sum(1 for t in self.trade_history if t.get("pnl", 0) < 0)
        win_rate = (wins / total * 100) if total > 0 else 0

        avg_trade = self.total_pnl / total if total > 0 else 0
        avg_win = np.mean([t["pnl"] for t in self.trade_history if t.get("pnl", 0) > 0]) if wins > 0 else 0
        avg_loss = np.mean([t["pnl"] for t in self.trade_history if t.get("pnl", 0) < 0]) if losses > 0 else 0

        gross_profit = sum(t["pnl"] for t in self.trade_history if t.get("pnl", 0) > 0)
        gross_loss = abs(sum(t["pnl"] for t in self.trade_history if t.get("pnl", 0) < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        returns = [t.get("pnl_percent", 0) for t in self.trade_history]
        sharpe = (
            np.mean(returns) / np.std(returns) * np.sqrt(365)
            if len(returns) > 1 and np.std(returns) > 0
            else 0
        )

        positive_returns = [r for r in returns if r > 0]
        negative_returns = [r for r in returns if r < 0]
        sortino = (
            np.mean(returns) / np.std(negative_returns) * np.sqrt(365)
            if negative_returns and np.std(negative_returns) > 0
            else 0
        )

        expectancy = (win_rate / 100 * avg_win) - ((1 - win_rate / 100) * abs(avg_loss))
        recovery_factor = abs(self.total_pnl / self.max_drawdown) if self.max_drawdown > 0 else 0

        return {
            "total_trades": total,
            "winning_trades": wins,
            "losing_trades": losses,
            "win_rate": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
            "total_pnl": round(self.total_pnl, 2),
            "daily_pnl": round(self.daily_pnl, 2),
            "weekly_pnl": round(self.weekly_pnl, 2),
            "monthly_pnl": round(self.monthly_pnl, 2),
            "average_trade": round(avg_trade, 2),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "max_drawdown": round(self.max_drawdown, 2),
            "sharpe_ratio": round(sharpe, 4),
            "sortino_ratio": round(sortino, 4),
            "expectancy": round(expectancy, 4),
            "recovery_factor": round(recovery_factor, 2),
            "consecutive_losses": self.consecutive_losses,
            "is_paused": self.is_paused,
        }
