import pytest

from src.risk.manager import RiskManager
from src.risk.sizing import PositionSizer


class TestRiskManager:
    def setup_method(self):
        self.rm = RiskManager()

    def test_can_trade_initial(self):
        assert self.rm.can_trade() is True

    def test_consecutive_losses_pause(self):
        for _ in range(self.rm.config["max_consecutive_losses"]):
            self.rm.record_trade({"pnl": -10})
        assert self.rm.consecutive_losses == self.rm.config["max_consecutive_losses"]
        assert self.rm.can_trade() is False

    def test_pause_trading(self):
        self.rm.pause_trading(duration_minutes=1)
        assert self.rm.is_paused is True

    def test_resume_trading(self):
        self.rm.pause_trading()
        self.rm.resume_trading()
        assert self.rm.is_paused is False

    def test_metrics(self):
        self.rm.record_trade({"pnl": 100})
        self.rm.record_trade({"pnl": 50})
        self.rm.record_trade({"pnl": -30})
        metrics = self.rm.get_metrics()
        assert metrics["total_trades"] == 3
        assert metrics["winning_trades"] == 2
        assert metrics["losing_trades"] == 1
        assert metrics["win_rate"] > 0


class TestPositionSizer:
    def setup_method(self):
        self.sizer = PositionSizer(balance=10000.0)

    def test_calculate_position_size(self):
        result = self.sizer.calculate_position_size(
            price=100.0, stop_loss=95.0
        )
        assert "position_size" in result
        assert "risk_amount" in result
        assert result["risk_amount"] > 0

    def test_calculate_stop_loss_long(self):
        sl = self.sizer.calculate_stop_loss(
            entry_price=100.0, atr=2.0, direction="long"
        )
        assert sl < 100.0

    def test_calculate_stop_loss_short(self):
        sl = self.sizer.calculate_stop_loss(
            entry_price=100.0, atr=2.0, direction="short"
        )
        assert sl > 100.0

    def test_calculate_take_profits(self):
        tps = self.sizer.calculate_take_profits(
            entry_price=100.0, stop_loss=95.0, direction="long"
        )
        assert len(tps) == 3
        assert all(tps[i] > 100 for i in tps)

    def test_calculate_take_profits_short(self):
        tps = self.sizer.calculate_take_profits(
            entry_price=100.0, stop_loss=105.0, direction="short"
        )
        assert len(tps) == 3
        assert all(tps[i] < 100 for i in tps)
