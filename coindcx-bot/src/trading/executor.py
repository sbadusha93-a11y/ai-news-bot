import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from loguru import logger

from src.config import bot_config, settings
from src.data.database import Database
from src.exchange.coindcx import CoinDCXExchange
from src.risk.manager import RiskManager
from src.risk.sizing import PositionSizer


TRADE_FEE_RATE = 0.00075  # 0.075% typical futures taker fee


class TradeExecutor:
    def __init__(
        self,
        exchange: CoinDCXExchange,
        risk_manager: RiskManager,
        position_sizer: PositionSizer,
        database: Optional[Database] = None,
    ):
        self.exchange = exchange
        self.risk_manager = risk_manager
        self.position_sizer = position_sizer
        self.database = database
        self.active_positions: Dict[str, Dict] = {}
        self.config = bot_config["bot"]

    async def execute_trade(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        confidence: float,
        quality_score: float,
        reason: str,
        df: Any = None,
    ) -> Optional[Dict]:
        if not self.risk_manager.can_trade():
            logger.warning(f"Cannot trade {symbol}: risk limits exceeded")
            return None

        if symbol in self.active_positions:
            logger.warning(f"Symbol {symbol} already has an active position, skipping duplicate")
            return None

        if len(self.active_positions) >= self.config["max_positions"]:
            logger.warning(f"Max positions ({self.config['max_positions']}) reached")
            return None

        atr = 0
        if df is not None and isinstance(df, dict):
            last_row = df.get("last_row", {})
            atr = last_row.get("atr", 0)
        stop_loss = self.position_sizer.calculate_stop_loss(
            entry_price, atr, direction
        )
        take_profits = self.position_sizer.calculate_take_profits(
            entry_price, stop_loss, direction
        )

        rr_1 = abs(take_profits.get(1, entry_price) - entry_price) / max(abs(entry_price - stop_loss), 1e-10)
        if rr_1 < bot_config["bot"]["min_rr"]:
            logger.warning(f"{symbol}: Risk reward {rr_1:.2f} below minimum {bot_config['bot']['min_rr']}")
            return None

        pos_size = self.position_sizer.calculate_position_size(
            entry_price, stop_loss
        )

        if "error" in pos_size:
            logger.error(f"Position sizing error for {symbol}: {pos_size['error']}")
            return None

        if entry_price <= 0 or stop_loss <= 0:
            logger.error(f"Invalid prices for {symbol}: entry={entry_price}, sl={stop_loss}")
            return None
        if direction not in ("long", "short"):
            logger.error(f"Invalid direction for {symbol}: {direction}")
            return None

        if settings.bot_mode == "paper":
            trade = await self._execute_paper_trade(
                symbol, direction, entry_price, stop_loss,
                take_profits, pos_size, confidence, quality_score, reason,
            )
        else:
            trade = await self._execute_live_trade(
                symbol, direction, entry_price, stop_loss,
                take_profits, pos_size, confidence, quality_score, reason,
            )

        if trade:
            trade.pop("id", None)
            if self.database:
                trade_id = await self.database.save_trade(trade)
                trade["db_trade_id"] = trade_id
                logger.info(f"Trade saved to DB: id={trade_id}")
            self.active_positions[symbol] = trade
            logger.info(f"Trade opened: {direction.upper()} {symbol} @ {entry_price}")

        return trade

    async def _execute_paper_trade(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profits: Dict,
        pos_size: Dict,
        confidence: float,
        quality_score: float,
        reason: str,
    ) -> Dict:
        return {
            "symbol": symbol,
            "side": direction,
            "entry_price": entry_price,
            "quantity": pos_size["position_size"],
            "stop_loss": stop_loss,
            "take_profit_1": take_profits.get(1, 0),
            "take_profit_2": take_profits.get(2, 0),
            "take_profit_3": take_profits.get(3, 0),
            "leverage": self.config["leverage"],
            "confidence_score": confidence,
            "trade_quality_score": quality_score,
            "risk_score": 100 - min(quality_score, 100),
            "reason_entry": reason,
            "status": "open",
            "entry_time": datetime.now(timezone.utc).isoformat(),
            "highest_price": entry_price if direction == "long" else 0,
            "lowest_price": entry_price if direction == "short" else 0,
            "trailing_stop_price": None,
            "break_even_price": None,
            "is_paper": True,
        }

    async def _execute_live_trade(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profits: Dict,
        pos_size: Dict,
        confidence: float,
        quality_score: float,
        reason: str,
    ) -> Optional[Dict]:
        active = await self.exchange.is_futures_active(symbol)
        if not active:
            logger.error(f"{symbol} futures instrument is not active, cannot place live order")
            return None
        try:
            order = await self.exchange.create_order(
                symbol, "limit", direction,
                pos_size["position_size"], entry_price,
                leverage=self.config["leverage"],
            )
            if not order:
                logger.error(f"Failed to place order for {symbol}")
                return None

            return {
                "symbol": symbol,
                "side": direction,
                "entry_price": entry_price,
                "quantity": pos_size["position_size"],
                "stop_loss": stop_loss,
                "take_profit_1": take_profits.get(1, 0),
                "take_profit_2": take_profits.get(2, 0),
                "take_profit_3": take_profits.get(3, 0),
                "leverage": self.config["leverage"],
                "order_id": order.get("id", ""),
                "confidence_score": confidence,
                "trade_quality_score": quality_score,
                "reason_entry": reason,
                "status": "open",
                "entry_time": datetime.now(timezone.utc).isoformat(),
                "highest_price": entry_price if direction == "long" else 0,
                "lowest_price": entry_price if direction == "short" else 0,
                "trailing_stop_price": None,
                "break_even_price": None,
                "is_paper": False,
            }
        except Exception as e:
            logger.error(f"Live trade execution failed for {symbol}: {e}")
            return None

    async def close_trade(
        self, symbol: str, exit_price: float, reason: str = "manual"
    ) -> Optional[Dict]:
        position = self.active_positions.pop(symbol, None)
        if not position:
            logger.warning(f"No active position for {symbol}")
            return None

        direction = position["side"]
        entry_price = position["entry_price"]
        quantity = position["quantity"]

        if settings.bot_mode == "live":
            try:
                order = await self.exchange.create_order(
                    symbol, "market",
                    "sell" if direction == "long" else "buy",
                    quantity, None,
                    leverage=self.config["leverage"],
                )
                if order:
                    fill_price = float(order.get("price_per_unit", order.get("avg_price", 0)))
                    if fill_price > 0:
                        exit_price = fill_price
            except Exception as e:
                logger.error(f"Failed to close live position for {symbol}: {e}")

        entry_fee = entry_price * quantity * TRADE_FEE_RATE
        exit_fee = exit_price * quantity * TRADE_FEE_RATE
        total_fees = entry_fee + exit_fee

        if direction == "long":
            gross_pnl = (exit_price - entry_price) * quantity
            pnl = gross_pnl - total_fees
            pnl_percent = ((exit_price - entry_price) / entry_price) * 100
        else:
            gross_pnl = (entry_price - exit_price) * quantity
            pnl = gross_pnl - total_fees
            pnl_percent = ((entry_price - exit_price) / entry_price) * 100

        tp_hit_level = None
        tp_hit_time = None
        if reason and reason.startswith("take_profit_"):
            try:
                tp_hit_level = int(reason.split("_")[-1])
                tp_hit_time = datetime.now(timezone.utc)
            except (ValueError, IndexError):
                pass

        trade_result = {
            **position,
            "exit_price": exit_price,
            "exit_time": datetime.now(timezone.utc).isoformat(),
            "pnl": round(pnl, 2),
            "pnl_percent": round(pnl_percent, 2),
            "reason_exit": reason,
            "tp_hit_level": tp_hit_level,
            "tp_hit_time": tp_hit_time.isoformat() if tp_hit_time else None,
            "status": "closed",
        }

        self.risk_manager.record_trade(trade_result)

        db_trade_id = position.get("db_trade_id")
        if db_trade_id and self.database:
            await self.database.update_trade(db_trade_id, {
                "status": "closed",
                "exit_price": exit_price,
                "exit_time": datetime.now(timezone.utc),
                "pnl": round(pnl, 2),
                "pnl_percent": round(pnl_percent, 2),
                "reason_exit": reason,
                "tp_hit_level": tp_hit_level,
                "tp_hit_time": tp_hit_time,
            })

        logger.info(f"Trade closed: {direction.upper()} {symbol} PnL: ${pnl:.2f} ({pnl_percent:.2f}%)")
        return trade_result

    async def close_all_positions(self, reason: str = "emergency"):
        results = []
        symbols = list(self.active_positions.keys())
        exit_prices = {}
        for symbol in symbols:
            try:
                ticker = await self.exchange.fetch_ticker(symbol)
                if ticker:
                    price = ticker.get("last", 0)
                    if price != 0:
                        exit_prices[symbol] = price
            except Exception:
                pass
        for symbol in symbols:
            exit_price = exit_prices.get(symbol)
            if exit_price is None or exit_price == 0:
                position = self.active_positions.get(symbol)
                if position:
                    logger.warning(f"Using entry_price as fallback exit for {symbol}")
                    exit_price = position["entry_price"]
            result = await self.close_trade(symbol, exit_price, reason)
            if result:
                results.append(result)
        return results

    def get_active_positions(self) -> List[Dict]:
        return list(self.active_positions.values())

    def get_position_count(self) -> int:
        return len(self.active_positions)
