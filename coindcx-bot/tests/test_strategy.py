import pytest

from src.strategy.scorer import TradeScorer
from src.strategy.analyzer import MarketAnalyzer


class TestTradeScorer:
    def setup_method(self):
        self.scorer = TradeScorer()

    def test_compute_signals_bullish(self):
        analysis = {
            "timeframes": {
                "4h": {
                    "technical_score": 30,
                    "smc_score": 20,
                    "volume_score": 15,
                    "price_action_score": 10,
                    "trend": "bullish",
                    "last_row": {
                        "rsi": 45,
                        "macd_signal_line": "bullish",
                        "ema_9_20_cross": "bullish",
                        "st_direction": "uptrend",
                        "volume": 5000,
                        "adx": 30,
                        "di_signal": "bullish",
                        "support": 95,
                        "resistance": 105,
                    },
                }
            },
            "overall": {
                "total_score": 75,
                "trend": "bullish",
                "trend_alignment": {"bullish": 1, "bearish": 0, "sideways": 0},
            },
        }

        signals = self.scorer.compute_signals(analysis)
        assert signals["direction"] == "long"
        assert signals["buy_probability"] > signals["sell_probability"]
        assert signals["confidence"] > 0

    def test_compute_signals_bearish(self):
        analysis = {
            "timeframes": {
                "4h": {
                    "technical_score": -30,
                    "smc_score": -20,
                    "volume_score": -15,
                    "price_action_score": -10,
                    "trend": "bearish",
                    "last_row": {
                        "rsi": 75,
                        "macd_signal_line": "bearish",
                        "ema_9_20_cross": "bearish",
                        "st_direction": "downtrend",
                        "volume": 5000,
                        "adx": 35,
                        "di_signal": "bearish",
                        "support": 95,
                        "resistance": 105,
                    },
                }
            },
            "overall": {
                "total_score": -75,
                "trend": "bearish",
                "trend_alignment": {"bullish": 0, "bearish": 1, "sideways": 0},
            },
        }

        signals = self.scorer.compute_signals(analysis)
        assert signals["direction"] == "short"


class TestMarketAnalyzer:
    def setup_method(self):
        self.analyzer = MarketAnalyzer()

    def test_rank_coins(self):
        analyses = {
            "BTC/USDT": {
                "signals": {
                    "direction": "long",
                    "confidence": 95,
                    "trade_quality": 85,
                    "risk_score": 20,
                },
                "overall": {"trend": "bullish"},
                "timeframes": {"4h": {"last_row": {"volume": 1000000}}},
            },
            "ETH/USDT": {
                "signals": {
                    "direction": "short",
                    "confidence": 80,
                    "trade_quality": 70,
                    "risk_score": 40,
                },
                "overall": {"trend": "bearish"},
                "timeframes": {"4h": {"last_row": {"volume": 500000}}},
            },
        }

        ranked = self.analyzer.rank_coins(analyses)
        assert len(ranked) == 2
        assert ranked[0]["rank_score"] >= ranked[1]["rank_score"]

    def test_filter_tradeable(self):
        ranked = [
            {"direction": "long", "confidence": 95, "risk_score": 20},
            {"direction": "short", "confidence": 85, "risk_score": 30},
            {"direction": "neutral", "confidence": 50, "risk_score": 60},
        ]
        tradeable = self.analyzer.filter_tradeable(ranked)
        assert len(tradeable) == 1
        assert tradeable[0]["direction"] == "long"
