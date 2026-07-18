#!/usr/bin/env python3
"""
CoinDCX Pro Bot - Institutional Grade AI Crypto Trading Platform
"""

import asyncio
import os
import signal
import sys
import traceback
import warnings
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
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
from src.data.signals_store import save_bot_signals
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
        self.ml_predictor = MLPredictor()
        self.strategy_engine = StrategyEngine(self.exchange, ml_predictor=self.ml_predictor)
        self.trade_scorer = TradeScorer()
        self.market_analyzer = MarketAnalyzer()
        self.ml_trainer = MLTrainer()
        self.trade_executor = TradeExecutor(
            self.exchange, self.risk_manager, self.position_sizer, database=self.database
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
            await self.database.close_stale_trades()
            open_trades = await self.database.get_open_trades()
            for t in open_trades:
                self.trade_executor.active_positions[t.symbol] = {
                    "symbol": t.symbol,
                    "side": t.side,
                    "entry_price": t.entry_price,
                    "quantity": t.quantity,
                    "stop_loss": t.stop_loss,
                    "take_profit_1": t.take_profit_1,
                    "take_profit_2": t.take_profit_2,
                    "take_profit_3": t.take_profit_3,
                    "leverage": t.leverage,
                    "confidence_score": t.confidence_score,
                    "trade_quality_score": t.trade_quality_score,
                    "risk_score": t.risk_score,
                    "reason_entry": t.reason_entry,
                    "status": "open",
                    "entry_time": t.entry_time.isoformat() if t.entry_time else None,
                    "highest_price": t.highest_price if t.highest_price is not None else (t.entry_price if t.side == "long" else 0),
                    "lowest_price": t.lowest_price if t.lowest_price is not None else (t.entry_price if t.side == "short" else 0),
                    "trailing_stop_active": bool(t.trailing_stop_active) if t.trailing_stop_active is not None else False,
                    "break_even_active": bool(t.break_even_active) if t.break_even_active is not None else False,
                    "is_paper": bool(t.is_paper) if t.is_paper is not None else True,
                    "db_trade_id": t.id,
                }
            logger.info(f"Database initialized — restored {len(open_trades)} open positions")
        except Exception as e:
            logger.warning(f"Database initialization failed (non-fatal): {e}")

        try:
            self.ml_predictor._ensure_loaded()
            logger.info("ML models loaded")
        except Exception as e:
            logger.info("No pre-trained ML models found (will train on data)")

        self.watchdog.add_health_check(self._health_check)
        self.watchdog.add_recovery_action("exchange", self._recover_exchange)
        self.watchdog.add_recovery_action("database", self._recover_database)
        self.watchdog.add_recovery_action("websocket", self._recover_websocket)
        asyncio.create_task(self.watchdog.start())

        set_bot_instance(self)
        logger.info("Bot initialization complete")

    async def _recover_exchange(self):
        logger.info("Attempting exchange recovery...")
        await self.exchange.close()
        self.exchange = CoinDCXExchange()
        self.data_fetcher = DataFetcher(self.exchange)
        self.strategy_engine = StrategyEngine(self.exchange, ml_predictor=self.ml_predictor)
        logger.success("Exchange recovery complete")
        await asyncio.sleep(2)

    async def _recover_database(self):
        logger.info("Attempting database recovery...")
        await self.database.close()
        self.database = Database()
        await self.database.initialize()
        logger.success("Database recovery complete")

    async def _recover_websocket(self):
        logger.info("Attempting WebSocket recovery...")
        await self.websocket.stop()
        self.websocket = CoinDCXWebSocket()
        asyncio.create_task(self.websocket.start())
        logger.success("WebSocket recovery complete")

    async def _health_check(self) -> bool:
        return self.running

    async def scan_market(self):
        logger.info("Scanning market...")
        markets = await self.data_fetcher.scan_all_markets()
        if markets.empty:
            fallback_symbols = bot_config.get("coin_selection", {}).get("whitelist", [])
            if not fallback_symbols:
                fallback_symbols = ["BTC_USDT", "ETH_USDT", "BNB_USDT", "SOL_USDT", "XRP_USDT",
                                     "ADA_USDT", "DOGE_USDT", "DOT_USDT", "LINK_USDT", "AVAX_USDT",
                                     "MATIC_USDT", "ATOM_USDT", "UNI_USDT", "LTC_USDT", "BCH_USDT",
                                     "XLM_USDT", "TRX_USDT", "FIL_USDT", "APT_USDT", "ARB_USDT"]
            import pandas as pd
            markets = pd.DataFrame({"symbol": fallback_symbols, "volume": [1]*len(fallback_symbols)})
            logger.info(f"No tickers from API, using {len(fallback_symbols)} fallback symbols")

        logger.info(f"Scanning {len(markets)} markets...")
        analyses = {}
        sentiment = {}
        symbols = markets['symbol'].tolist()
        sem = asyncio.Semaphore(10)

        async def _do_one(symbol):
            async with sem:
                for attempt in range(2):
                    try:
                        df_dict = await asyncio.wait_for(
                            self.data_fetcher.fetch_multi_timeframe_data(symbol),
                            timeout=60,
                        )
                        if not df_dict or all(df.empty for df in df_dict.values()):
                            return None
                        analysis = await self.strategy_engine.analyze_symbol(symbol, df_dict)
                        analysis["sentiment"] = sentiment
                        return symbol, analysis
                    except asyncio.TimeoutError:
                        logger.debug(f"Timeout {symbol}")
                        return None
                    except Exception as e:
                        if attempt == 0:
                            logger.debug(f"Retry {symbol} after error: {e}")
                            await asyncio.sleep(1)
                        else:
                            logger.debug(f"Error {symbol}: {e}")
                            return None

        results = await asyncio.gather(*[_do_one(s) for s in symbols])
        for r in results:
            if r:
                symbol, analysis = r
                analyses[symbol] = analysis

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

        save_bot_signals(self.last_ranked)
        return self.last_ranked

    async def execute_signals(self):
        if not bot_config["bot"]["auto_trade"]:
            logger.debug("Auto-trade disabled, skipping signal execution")
            return
        if not self.risk_manager.can_trade():
            logger.warning("Circuit breaker active: risk limits exceeded, skipping signal execution")
            return

        max_dd = self.risk_manager.get_metrics().get("max_drawdown", 0)
        if max_dd >= bot_config["risk"]["max_drawdown"]:
            logger.critical(f"Max drawdown {max_dd:.1f}% ≥ limit, closing all positions")
            await self.trade_executor.close_all_positions("max_drawdown_hit")
            return

        for opp in self.last_ranked[:bot_config["coin_selection"]["trade_top_n"]]:
            if opp["direction"] not in ("long", "short"):
                continue
            if opp["confidence"] < bot_config["bot"]["min_confidence"]:
                continue
            if opp["symbol"] in self.trade_executor.active_positions:
                logger.debug(f"Symbol {opp['symbol']} already active, skipping duplicate signal")
                continue

            active = await self.exchange.is_futures_active(opp["symbol"])
            if not active:
                logger.warning(f"{opp['symbol']} futures instrument is not active, skipping")
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

            await asyncio.sleep(1)

    async def _run_monitor(self):
        while self.running:
            try:
                if self.trade_executor.active_positions:
                    await asyncio.wait_for(
                        self.position_monitor.monitor_positions(
                            self.trade_executor.active_positions
                        ),
                        timeout=60,
                    )
            except asyncio.TimeoutError:
                logger.warning("Position monitor cycle timed out")
            except Exception as e:
                logger.error(f"Position monitor error: {e}")
            await asyncio.sleep(10)

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
        except (httpx.ConnectError, httpx.RemoteProtocolError, OSError) as e:
            logger.error(f"Network error in cycle: {e}\n{traceback.format_exc()}")
            await self.watchdog.recover_from("exchange", e)
        except Exception as e:
            logger.error(f"Cycle error: {e}\n{traceback.format_exc()}")

        now = datetime.now(timezone.utc)
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
        asyncio.create_task(self._run_monitor())

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
                logger.error(f"Fatal error in main loop: {e}\n{traceback.format_exc()}")
                await asyncio.sleep(60)

    async def stop(self):
        logger.info("Shutting down bot...")
        self.running = False
        self.position_monitor.stop()
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
        if settings.railway_lite_mode:
            logger.info("Running in Railway lite mode — memory optimizations active")

        if "--api" in sys.argv:
            logger.info("Starting API server...")
            api_task = asyncio.create_task(
                uvicorn.Server(
                    uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")), log_level="info")
                ).serve()
            )
            bot_task = asyncio.create_task(bot.start())
            done, pending = await asyncio.wait(
                [api_task, bot_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
        else:
            await bot.start()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Received shutdown signal")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
