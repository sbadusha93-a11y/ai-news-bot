from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Portfolio:
    balance: float = 10000.0
    initial_balance: float = 10000.0
    total_pnl: float = 0.0
    open_positions: Dict[str, Dict] = field(default_factory=dict)
    trade_history: List[Dict] = field(default_factory=list)

    def update_balance(self):
        self.total_pnl = self.balance - self.initial_balance

    def add_position(self, symbol: str, position: Dict):
        self.open_positions[symbol] = position

    def remove_position(self, symbol: str) -> Optional[Dict]:
        return self.open_positions.pop(symbol, None)

    def add_trade(self, trade: Dict):
        self.trade_history.append(trade)

    def get_exposure(self) -> float:
        total_exposure = sum(
            p.get("quantity", 0) * p.get("entry_price", 0)
            for p in self.open_positions.values()
        )
        return (total_exposure / self.balance * 100) if self.balance > 0 else 0

    def get_positions_count(self) -> int:
        return len(self.open_positions)

    def get_metrics(self) -> Dict:
        total = len(self.trade_history)
        wins = sum(1 for t in self.trade_history if t.get("pnl", 0) > 0)
        losses = sum(1 for t in self.trade_history if t.get("pnl", 0) < 0)

        return {
            "balance": round(self.balance, 2),
            "total_pnl": round(self.total_pnl, 2),
            "open_positions": self.get_positions_count(),
            "exposure": round(self.get_exposure(), 2),
            "total_trades": total,
            "winning_trades": wins,
            "losing_trades": losses,
            "win_rate": round(wins / total * 100, 2) if total > 0 else 0,
        }
