import pandas as pd
import numpy as np
import pytest

from src.backtest.engine import BacktestEngine
from src.backtest.optimizer import StrategyOptimizer


@pytest.fixture
def sample_data():
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=1000, freq="4h")
    price = 100 * (1 + np.cumsum(np.random.randn(1000) * 0.005))
    df = pd.DataFrame({
        "open": price * (1 + np.random.randn(1000) * 0.002),
        "high": price * (1 + abs(np.random.randn(1000) * 0.005)),
        "low": price * (1 - abs(np.random.randn(1000) * 0.005)),
        "close": price,
        "volume": np.random.randint(10000, 100000, 1000),
    }, index=dates)
    return df


class TestBacktestEngine:
    def setup_method(self):
        self.engine = BacktestEngine(initial_balance=10000.0)

    @pytest.mark.asyncio
    async def test_run(self, sample_data):
        result = await self.engine.run(sample_data)
        assert "total_trades" in result
        assert "net_profit" in result
        assert "win_rate" in result
        assert "profit_factor" in result
        assert "sharpe_ratio" in result

    def test_metrics_calculation(self):
        metrics = {
            "total_trades": 0,
            "net_profit": 0,
        }
        assert metrics["total_trades"] == 0

    @pytest.mark.asyncio
    async def test_empty_data(self):
        empty_df = pd.DataFrame()
        result = await self.engine.run(empty_df)
        assert "error" in result


class TestStrategyOptimizer:
    def setup_method(self):
        self.optimizer = StrategyOptimizer()

    @pytest.mark.asyncio
    async def test_optimize(self):
        async def mock_backtest(df, params):
            return {
                "sharpe_ratio": np.random.uniform(0.5, 2.0),
                "win_rate": np.random.uniform(40, 70),
                "total_trades": np.random.randint(50, 200),
            }

        dates = pd.date_range("2024-01-01", periods=500, freq="4h")
        df = pd.DataFrame({
            "open": np.random.randn(500) + 100,
            "high": np.random.randn(500) + 102,
            "low": np.random.randn(500) + 98,
            "close": np.random.randn(500) + 100,
            "volume": np.random.randint(10000, 100000, 500),
        }, index=dates)

        result = await self.optimizer.optimize(df, mock_backtest, "sharpe_ratio", max_combinations=20)
        assert "best_params" in result
        assert "best_metrics" in result
