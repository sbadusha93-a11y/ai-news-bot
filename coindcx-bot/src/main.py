#!/usr/bin/env python3

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

from src.config import bot_config, settings, validate_config
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
from src.risk.regime import MarketRegimeDetector
from src.risk.portfolio import PortfolioRiskManager
from src.trading.executor import TradeExecutor
from src.trading.monitor import PositionMonitor
from src.trading.orders import SmartOrderManager
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
        self.portfolio_risk = PortfolioRiskManager(
            max_leverage=bot_config["bot"]["leverage"]
        )
        self.ml_predictor = MLPredictor()
        self.strategy_engine = StrategyEngine(self.exchange, ml_predictor=self.ml_predictor)
        self.trade_scorer = TradeScorer()
        self.market_analyzer = MarketAnalyzer()
        self.ml_trainer = MLTrainer()
        self.trade_executor = TradeExecutor(
            self.exchange, self.risk_manager, self.position_sizer, database=self.database
        )
        self.smart_orders = SmartOrderManager(
            create_order_fn=self.exchange.create_order,
            cancel_order_fn=self.exchange.cancel_order,
            fetch_order_fn=None,
            fill_timeout=30.0,
            poll_interval=2.0,
        )
        self.position_monitor = PositionMonitor(
            self.exchange, self.risk_manager, self.position_sizer,
            self.trade_executor.close_trade,
        )
        self.backtest_engine = BacktestEngine()
        self.strategy_optimizer = StrategyOptimizer()
        self.regime_detector = MarketRegimeDetector()
        self.watchdog = Watchdog()
        self.last_ranked: List[Dict] = []
        self._scan_in_progress = False
        self._last_regime: Dict = {}
        self._market_regime_cache: Dict[str, Dict] = {}

    async def initialize(self):
        logger.info("Initializing CoinDCX Pro Bot v3.0...")

        config_warnings = validate_config()
        for warning in config_warnings:
            logger.warning(f"Config: {warning}")

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
                    "trailing_stop_price": getattr(t, 'trailing_stop_price', None),
                    "break_even_price": getattr(t, 'break_even_price', None),
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

        if settings.bot_mode == "live":
            try:
                exchange_ok = await self.exchange.check_exchange_status()
                if not exchange_ok:
                    logger.critical("Exchange status check FAILED — exchange may be unreachable")
                else:
                    logger.info("Exchange status: OK")
                await self.reconcile_positions()
            except Exception as e:
                logger.warning(f"Live trading pre-checks failed (non-fatal): {e}")

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
                        analysis["sentiment"] = dict(sentiment)
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
                if analysis.get("regime"):
                    self._market_regime_cache[symbol] = analysis["regime"]

        self._update_global_regime(analyses)

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

        regime = self._last_regime
        logger.info(f"Market regime: {regime.get('trend','?')} | "
                     f"Vol: {regime.get('volatility','?')} | "
                     f"Tradeable: {regime.get('is_tradeable', True)}")

        save_bot_signals(self.last_ranked)
        return self.last_ranked

    def _update_global_regime(self, analyses: Dict):
        trends = {}
        vols = {}
        for sym, an in analyses.items():
            r = an.get("regime", {})
            t = r.get("trend", "sideways")
            trends[t] = trends.get(t, 0) + 1
            v = r.get("volatility", "normal")
            vols[v] = vols.get(v, 0) + 1
        maj_trend = max(trends, key=trends.get) if trends else "sideways"
        maj_vol = max(vols, key=vols.get) if vols else "normal"

        regime_config = bot_config["risk"].get("regime", {})
        is_tradeable = True
        if regime_config.get("enabled", True):
            if maj_vol == "extreme":
                is_tradeable = False
            elif maj_trend in ("sideways",) and regime_config.get("adapt_confidence", True):
                is_tradeable = False

        self._last_regime = {
            "trend": maj_trend,
            "volatility": maj_vol,
            "is_tradeable": is_tradeable,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def reconcile_positions(self):
        if settings.bot_mode != "live":
            return
        try:
            exchange_positions = await self.exchange.fetch_positions()
            if not exchange_positions:
                return
            exchange_symbols = {}
            for ep in exchange_positions:
                pair = ep.get("market", ep.get("pair", ""))
                if "USDT" in pair or "usdt" in pair:
                    sym = pair.replace("-", "_").replace("B_", "").replace("B-", "")
                    parts = sym.split("_")
                    if len(parts) == 2:
                        pass
                    else:
                        for q in ["USDT", "BTC", "USDC"]:
                            if q in sym and sym.index(q) > 0:
                                idx = sym.index(q)
                                sym = sym[:idx] + "_" + sym[idx:]
                                break
                    quantity = float(ep.get("size", ep.get("quantity", 0)))
                    if quantity > 0:
                        exchange_symbols[sym] = {
                            "quantity": quantity,
                            "side": "long" if float(ep.get("size", 0)) > 0 else "short",
                            "entry_price": float(ep.get("entry_price", ep.get("avg_price", 0))),
                        }
            for sym in list(self.trade_executor.active_positions.keys()):
                if sym not in exchange_symbols:
                    logger.warning(f"Position {sym} in DB but not on exchange — removing")
                    pos = self.trade_executor.active_positions.pop(sym, None)
                    if pos and self.database:
                        await self.database.update_trade(
                            pos.get("db_trade_id"),
                            {"status": "closed", "reason_exit": "reconciliation_removed"}
                        )
            for sym, ep in exchange_symbols.items():
                if sym not in self.trade_executor.active_positions:
                    logger.info(f"Position {sym} on exchange but not in DB — restoring")
                    self.trade_executor.active_positions[sym] = {
                        "symbol": sym,
                        "side": ep["side"],
                        "entry_price": ep["entry_price"],
                        "quantity": ep["quantity"],
                        "status": "open",
                        "stop_loss": 0,
                        "take_profit_1": 0,
                        "is_paper": False,
                        "entry_time": datetime.now(timezone.utc).isoformat(),
                    }
            if exchange_symbols:
                logger.info(f"Position reconciliation complete: {len(self.trade_executor.active_positions)} tracked")
        except Exception as e:
            logger.warning(f"Position reconciliation failed (non-fatal): {e}")

    async def execute_signals(self):
        if not bot_config["bot"]["auto_trade"]:
            logger.debug("Auto-trade disabled, skipping signal execution")
            return
        if not self.risk_manager.can_trade():
            logger.warning("Circuit breaker active: risk limits exceeded, skipping signal execution")
            return
        regime = self._last_regime
        if regime.get("volatility") == "extreme" and not regime.get("is_tradeable", True):
            cooldown = bot_config["risk"].get("regime", {}).get("extreme_volatility_cooldown_minutes", 30)
            logger.warning(f"Extreme volatility detected — pausing trades for {cooldown}m")
            self.risk_manager.pause_trading(duration_minutes=cooldown)
            return

        max_dd = self.risk_manager.get_metrics().get("max_drawdown", 0)
        if max_dd >= bot_config["risk"]["max_drawdown"]:
            logger.critical(f"Max drawdown {max_dd:.1f}% ≥ limit, closing all positions and pausing trading")
            await self.trade_executor.close_all_positions("max_drawdown_hit")
            self.risk_manager.pause_trading(duration_minutes=bot_config["risk"].get("pause_duration_minutes", 60))
            return

        if self.trade_executor.active_positions:
            corr_result = await self._check_portfolio_risk()
            if not corr_result.get("is_safe", True):
                logger.warning(f"Portfolio risk violations: {corr_result['violations']}")
                if any(v.get("risk") == "high_correlation_same_direction" for v in corr_result["violations"]):
                    logger.warning("Correlated positions detected — not opening new positions")
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

    async def _check_portfolio_risk(self) -> Dict:
        positions = self.trade_executor.active_positions
        price_data = {}
        for sym in positions:
            try:
                ticker = await self.exchange.fetch_ticker(sym)
                if ticker:
                    price_data[sym] = ticker.get("last", 0)
            except Exception:
                continue
        if len(price_data) < 2:
            return {"is_safe": True, "violations": []}

        price_series = {}
        for sym in price_data:
            try:
                hist = await self.data_fetcher.fetch_historical_data(sym, "1h", limit=100)
                if not hist.empty:
                    price_series[sym] = hist["close"]
            except Exception:
                continue
        if len(price_series) >= 2:
            self.portfolio_risk.compute_correlation_matrix(price_series)

        corr_result = self.portfolio_risk.check_correlation_risk(
            positions,
            correlation_threshold=bot_config["risk"].get("portfolio", {}).get("correlation_threshold", 0.70),
            max_correlated_exposure=bot_config["risk"].get("portfolio", {}).get("max_correlated_exposure", 0.40),
        )
        return corr_result

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
            await asyncio.sleep(1)

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
        logger.info(f"Bot started in {settings.bot_mode.upper()} mode | v3.0")

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

                if settings.bot_mode == "live" and cycle_count % 10 == 0:
                    asyncio.create_task(self.reconcile_positions())

                await asyncio.sleep(bot_config["timeframes"].get("scan_interval", 900))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Fatal error in main loop: {e}\n{traceback.format_exc()}")
                await asyncio.sleep(60)

    async def stop(self):
        logger.info("Shutting down bot v3.0...")
        self.running = False
        if bot_config["bot"]["mode"] == "paper":
            logger.info("Paper mode — NOT closing positions on shutdown")
        else:
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
                    uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", "8085")), log_level="info")
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
