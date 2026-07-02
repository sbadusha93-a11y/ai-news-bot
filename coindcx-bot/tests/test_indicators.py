import pandas as pd
import numpy as np
import pytest

from src.indicators.technical import TechnicalIndicators
from src.indicators.smc import SMCIndicators
from src.indicators.volume import VolumeIndicators
from src.indicators.price_action import PriceActionIndicators


@pytest.fixture
def sample_df():
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=500, freq="4h")
    price = 100 * (1 + np.cumsum(np.random.randn(500) * 0.01))
    df = pd.DataFrame({
        "open": price * (1 + np.random.randn(500) * 0.005),
        "high": price * (1 + abs(np.random.randn(500) * 0.01)),
        "low": price * (1 - abs(np.random.randn(500) * 0.01)),
        "close": price,
        "volume": np.random.randint(1000, 10000, 500),
    }, index=dates)
    return df


class TestTechnicalIndicators:
    def setup_method(self):
        self.indicator = TechnicalIndicators()

    def test_rsi(self, sample_df):
        result = self.indicator._rsi(sample_df.copy())
        assert "rsi" in result.columns
        assert result["rsi"].between(0, 100).all()

    def test_macd(self, sample_df):
        result = self.indicator._macd(sample_df.copy())
        assert "macd" in result.columns
        assert "macd_signal" in result.columns
        assert "macd_histogram" in result.columns

    def test_ema(self, sample_df):
        result = self.indicator._ema(sample_df.copy())
        assert "ema_9" in result.columns
        assert "ema_20" in result.columns
        assert "ema_50" in result.columns

    def test_bollinger_bands(self, sample_df):
        result = self.indicator._bollinger_bands(sample_df.copy())
        assert "bb_upper" in result.columns
        assert "bb_middle" in result.columns
        assert "bb_lower" in result.columns
        assert (result["bb_upper"] >= result["bb_lower"]).all()

    def test_atr(self, sample_df):
        result = self.indicator._atr(sample_df.copy())
        assert "atr" in result.columns
        assert (result["atr"] >= 0).all()

    def test_adx(self, sample_df):
        result = self.indicator._adx(sample_df.copy())
        assert "adx" in result.columns
        assert result["adx"].between(0, 100).all()

    def test_supertrend(self, sample_df):
        result = self.indicator._supertrend(sample_df.copy())
        assert "st_trend" in result.columns
        assert "st_direction" in result.columns

    def test_compute_all(self, sample_df):
        result = self.indicator.compute_all(sample_df.copy())
        assert not result.empty
        assert len(result.columns) > 10


class TestSMCIndicators:
    def setup_method(self):
        self.indicator = SMCIndicators()

    def test_swing_points(self, sample_df):
        result = self.indicator._swing_points(sample_df.copy())
        assert "swing_high" in result.columns
        assert "swing_low" in result.columns

    def test_break_of_structure(self, sample_df):
        df = self.indicator._swing_points(sample_df.copy())
        result = self.indicator._break_of_structure(df)
        assert "bos" in result.columns

    def test_order_blocks(self, sample_df):
        result = self.indicator._order_blocks(sample_df.copy())
        assert "order_block" in result.columns

    def test_fair_value_gaps(self, sample_df):
        result = self.indicator._fair_value_gaps(sample_df.copy())
        assert "fvg" in result.columns

    def test_get_smc_score(self, sample_df):
        df = self.indicator.compute_all(sample_df.copy())
        score = self.indicator.get_smc_score(df)
        assert isinstance(score, float)


class TestVolumeIndicators:
    def setup_method(self):
        self.indicator = VolumeIndicators()

    def test_obv(self, sample_df):
        result = self.indicator._obv(sample_df.copy())
        assert "obv" in result.columns

    def test_cmf(self, sample_df):
        result = self.indicator._cmf(sample_df.copy())
        assert "cmf" in result.columns

    def test_mfi(self, sample_df):
        result = self.indicator._mfi(sample_df.copy())
        assert "mfi" in result.columns
        assert result["mfi"].between(0, 100).all()

    def test_volume_spike(self, sample_df):
        result = self.indicator._volume_spike(sample_df.copy())
        assert "volume_spike" in result.columns

    def test_get_volume_score(self, sample_df):
        df = self.indicator.compute_all(sample_df.copy())
        score = self.indicator.get_volume_score(df)
        assert isinstance(score, float)


class TestPriceActionIndicators:
    def setup_method(self):
        self.indicator = PriceActionIndicators()

    def test_candlestick_patterns(self, sample_df):
        result = self.indicator._candlestick_patterns(sample_df.copy())
        assert "bullish_engulfing" in result.columns
        assert "bearish_engulfing" in result.columns

    def test_support_resistance(self, sample_df):
        df = sample_df.copy()
        df["swing_high"] = False
        df["swing_low"] = False
        result = self.indicator._support_resistance(df)
        assert "support" in result.columns
        assert "resistance" in result.columns
