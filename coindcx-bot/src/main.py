#!/usr/bin/env python3
"""
CoinDCX Pro Bot - Institutional Grade AI Crypto Trading Platform
"""

import asyncio
import signal
import sys
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
warnings.filterwarnings("ignore", category=RuntimeWarning)
np.seterr(invalid="ignore")

import uvicorn
from loguru import logger

from src.config import bot_config, settings
from src.exchange.coindcx import CoinDCXExchange
from src.exchange.websocket import CoinDCXWebSocket
from src.data.fetcher import DataFetcher
from src.data.cache import DataCache
from src.data.database import Database
from src.strategy.engine import StrategyEngine
from src.strategy.scorer import TradeScorer
from src.strategy.analyzer import MarketAnalyzer
from src.ml.trainer import MLTrainer
from src.ml.predictor import MLPredictor
from src.risk.manager import RiskManager
from src.risk.sizing import PositionSizer
from src.trading.executor import TradeExecutor
from src.trading.monitor import PositionMonitor
from src.trading.portfolio import Portfolio
from src.backtest.engine import BacktestEngine
from src.backtest.optimizer import StrategyOptimizer
from src.alerts.telegram import TelegramAlert
from src.alerts.discord import DiscordAlert
from src.alerts.email import EmailAlert
from src.alerts.notification import DesktopNotification
from src.utils.logger import setup_logger
from src.utils.watchdog import Watchdog
from src.api.server import app, set_bot_instance


class CoinDCXBot:
    def __init__(self):
        self.logger = setup_logger()
        self.running = False

        self.exchange = CoinDCXExchange()
        self.websocket = CoinDCXWebSocket()
        self.data_fetcher = DataFetcher(self.exchange)
        self.data_cache = DataCache()
        self.database = Database()
        self.telegram = TelegramAlert()
        self.discord = DiscordAlert()
        self.email = EmailAlert()
        self.notification = DesktopNotification()
        self.risk_manager = RiskManager()
        self.position_sizer = PositionSizer()
        self.strategy_engine = StrategyEngine(self.exchange)
        self.trade_scorer = TradeScorer()
        self.market_analyzer = MarketAnalyzer()
        self.ml_trainer = MLTrainer()
        self.ml_predictor = MLPredictor()
        self.trade_executor = TradeExecutor(
            self.exchange, self.risk_manager, self.position_sizer
        )
        self.position_monitor = PositionMonitor(
            self.exchange, self.risk_manager, self.position_sizer,
            self.trade_executor.close_trade,
        )
        self.backtest_engine = BacktestEngine()
        self.strategy_optimizer = StrategyOptimizer()
        self.watchdog = Watchdog()
        self.last_ranked: List[Dict] = []

    async def initialize(self):
        logger.info("Initializing CoinDCX Pro Bot...")

        try:
            await self.database.initialize()
            logger.info("Database initialized")
        except Exception as e:
            logger.warning(f"Database initialization failed (non-fatal): {e}")

        try:
            self.ml_predictor._ensure_loaded()
            logger.info("ML models loaded")
        except Exception as e:
            logger.info("No pre-trained ML models found (will train on data)")

        self.watchdog.add_health_check(self._health_check)
        asyncio.create_task(self.watchdog.start())

        set_bot_instance(self)
        logger.info("Bot initialization complete")

    async def _health_check(self) -> bool:
        return self.running

    async def scan_market(self):
        logger.info("Scanning market...")
        markets = await self.data_fetcher.scan_all_markets()
        if markets.empty:
            logger.warning("No markets found")
            return

        logger.info(f"Scanning {len(markets)} markets...")
        analyses = {}

        for _, row in markets.iterrows():
            symbol = row["symbol"]
            try:
                df_dict = await self.data_fetcher.fetch_multi_timeframe_data(symbol)
                if not df_dict:
                    continue

                analysis = await self.strategy_engine.analyze_symbol(symbol, df_dict)
                sentiment = await self.data_fetcher.fetch_sentiment_data()
                analysis["sentiment"] = sentiment
                analyses[symbol] = analysis

                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue

        ranked = self.market_analyzer.rank_coins(analyses)
        self.last_ranked = self.market_analyzer.select_top_opportunities(
            ranked, top_n=bot_config["coin_selection"]["top_n_ranked"]
        )

        logger.info(f"Top opportunities: {len(self.last_ranked)}")
        for opp in self.last_ranked[:bot_config["coin_selection"]["trade_top_n"]]:
            logger.info(
                f"  {opp['symbol']}: {opp['direction'].upper()} "
                f"(Conf: {opp['confidence']:.1f}%, Risk: {opp['risk_score']:.1f}%)"
            )

        return self.last_ranked

    async def execute_signals(self):
        for opp in self.last_ranked[:bot_config["coin_selection"]["trade_top_n"]]:
            if opp["direction"] not in ("long", "short"):
                continue
            if opp["confidence"] < bot_config["bot"]["min_confidence"]:
                continue

            trade = await self.trade_executor.execute_trade(
                symbol=opp["symbol"],
                direction=opp["direction"],
                entry_price=opp["analysis"]["timeframes"]
                    .get(bot_config["timeframes"]["primary"], {})
                    .get("last_row", {})
                    .get("close", 0),
                confidence=opp["confidence"],
                quality_score=opp["trade_quality"],
                reason=opp["analysis"].get("signals", {}).get("reason", "AI decision"),
                df=opp["analysis"]["timeframes"]
                    .get(bot_config["timeframes"]["primary"], {}),
            )

            if trade:
                await self.telegram.send_trade_alert(trade)
                await self.discord.send_trade_alert(trade)
                await self.notification.send_trade_alert(trade)

                await self.database.save_trade(trade)

            await asyncio.sleep(1)

    async def monitor_positions(self):
        if self.trade_executor.active_positions:
            await self.position_monitor.monitor_positions(
                self.trade_executor.active_positions
            )

    async def train_ml(self, symbols: List[str]):
        if not settings.ml_training_enabled:
            return

        logger.info("Starting ML training...")
        dfs = {}
        for symbol in symbols[:10]:
            df = await self.data_fetcher.fetch_historical_data(
                symbol, "4h", limit=1000
            )
            if not df.empty:
                dfs[symbol] = df

        result = await self.ml_trainer.train(dfs, symbols)
        logger.info(f"ML training result: {result}")

    async def run_cycle(self):
        logger.info("Starting market analysis cycle...")
        try:
            await self.scan_market()
            await self.execute_signals()
            await self.monitor_positions()
        except Exception as e:
            logger.error(f"Cycle error: {e}")

        now = datetime.utcnow()
        if now.hour == 0 and now.minute < 5:
            self.risk_manager.reset_daily()
        if now.weekday() == 0 and now.hour == 0 and now.minute < 5:
            self.risk_manager.reset_weekly()
        if now.day == 1 and now.hour == 0 and now.minute < 5:
            self.risk_manager.reset_monthly()

    async def start(self):
        self.running = True
        await self.initialize()
        logger.info(f"Bot started in {settings.bot_mode.upper()} mode")

        asyncio.create_task(self.websocket.start())

        cycle_count = 0
        while self.running:
            try:
                await self.run_cycle()
                cycle_count += 1

                if cycle_count % 24 == 0:
                    symbols = [opp["symbol"] for opp in self.last_ranked]
                    asyncio.create_task(self.train_ml(symbols))

                await asyncio.sleep(bot_config["timeframes"].get("scan_interval", 900))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Fatal error in main loop: {e}")
                await asyncio.sleep(60)

    async def stop(self):
        logger.info("Shutting down bot...")
        self.running = False
        await self.trade_executor.close_all_positions("bot_shutdown")
        await self.websocket.stop()
        await self.data_cache.close()
        await self.database.close()
        await self.telegram.close()
        await self.discord.close()
        await self.data_fetcher.close()
        await self.strategy_engine.close()
        await self.exchange.close()
        await self.watchdog.stop()
        logger.info("Bot shutdown complete")


async def main():
    bot = CoinDCXBot()
    try:
        if "--api" in sys.argv:
            logger.info("Starting API server...")
            api_task = asyncio.create_task(
                uvicorn.Server(
                    uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
                ).serve()
            )
            bot_task = asyncio.create_task(bot.start())
            await asyncio.gather(api_task, bot_task)
        else:
            await bot.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
