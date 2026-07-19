import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from src.exchange.coindcx import CoinDCXExchange
from src.risk.manager import RiskManager
from src.risk.sizing import PositionSizer


class PositionMonitor:
    def __init__(
        self,
        exchange: CoinDCXExchange,
        risk_manager: RiskManager,
        position_sizer: PositionSizer,
        on_close: Optional[Callable] = None,
    ):
        self.exchange = exchange
        self.risk_manager = risk_manager
        self.position_sizer = position_sizer
        self.on_close = on_close
        self._running = False

    async def monitor_positions(self, positions: Dict[str, Dict]):
        if not positions:
            return
        all_tickers = await self.exchange.fetch_all_tickers()
        if not all_tickers:
            return

        prices = {}
        for symbol, position in list(positions.items()):
            try:
                ticker = all_tickers.get(symbol)
                if not ticker:
                    continue

                current_price = ticker.get("last", 0)
                if current_price == 0:
                    continue
                prices[symbol] = current_price

                self.update_trailing_stops({symbol: position}, {symbol: current_price})

                action = self._evaluate_exit(position, current_price)
                if action:
                    logger.info(f"Exit signal for {symbol}: {action['reason']}")
                    if self.on_close:
                        await self.on_close(symbol, current_price, action["reason"])

            except Exception as e:
                logger.error(f"Error monitoring {symbol}: {e}")

    def _position_price(self, position: Dict, current_price: float) -> float:
        """Returns the effective price for exit evaluation.
        Paper mode: tracks market delta from first observation (live-like behavior).
        Live mode: uses current_price directly.
        """
        if not position.get("is_paper", False):
            return current_price

        entry = position["entry_price"]
        first = position.get("paper_first_price")

        if first is None:
            position["paper_first_price"] = current_price
            return entry

        return entry + (current_price - first)

    def _evaluate_exit(
        self, position: Dict, current_price: float
    ) -> Optional[Dict]:
        direction = position["side"]
        entry = position["entry_price"]
        sl = position["stop_loss"]
        tp1 = position.get("take_profit_1", 0)
        tp2 = position.get("take_profit_2", 0)
        tp3 = position.get("take_profit_3", 0)

        price = self._position_price(position, current_price)

        if direction == "long":
            if price <= sl:
                return {"reason": "stop_loss"}
            if tp3 > 0 and price >= tp3:
                return {"reason": "take_profit_3"}
            if tp2 > 0 and price >= tp2:
                return {"reason": "take_profit_2"}
            if tp1 > 0 and price >= tp1:
                return {"reason": "take_profit_1"}
        else:
            if price >= sl:
                return {"reason": "stop_loss"}
            if tp3 > 0 and price <= tp3:
                return {"reason": "take_profit_3"}
            if tp2 > 0 and price <= tp2:
                return {"reason": "take_profit_2"}
            if tp1 > 0 and price <= tp1:
                return {"reason": "take_profit_1"}

        # trailing stop
        if position.get("trailing_stop_active"):
            trailing = position.get("trailing_stop_price", sl)
            if (direction == "long" and price <= trailing) or \
               (direction == "short" and price >= trailing):
                return {"reason": "trailing_stop"}

        if position.get("break_even_active"):
            be = position.get("break_even_price", entry)
            if (direction == "long" and price <= be) or \
               (direction == "short" and price >= be):
                return {"reason": "break_even"}

        return None

    def update_trailing_stops(
        self, positions: Dict[str, Dict], current_prices: Dict[str, float]
    ):
        for symbol, position in positions.items():
            if symbol not in current_prices:
                continue

            price = current_prices[symbol]
            direction = position["side"]
            entry = position["entry_price"]
            sl = position["stop_loss"]

            pos_price = self._position_price(position, price)

            if direction == "long":
                if pos_price > position.get("highest_price", entry):
                    position["highest_price"] = pos_price
                    new_sl, activated = self.position_sizer.calculate_trailing_stop(
                        pos_price, entry, 0, direction,
                        position["highest_price"], None,
                    )
                    if activated:
                        position["trailing_stop_active"] = True
                        position["trailing_stop_price"] = new_sl

            be_price, be_activated = self.position_sizer.calculate_break_even_stop(
                pos_price, entry, direction,
            )
            if be_activated:
                position["break_even_active"] = True
                position["break_even_price"] = be_price

    async def start_monitoring(self, positions: Dict[str, Dict]):
        self._running = True
        while self._running:
            if positions:
                current_prices = {}
                for symbol in positions:
                    ticker = await self.exchange.fetch_ticker(symbol)
                    if ticker:
                        current_prices[symbol] = ticker.get("last", 0)

                self.update_trailing_stops(positions, current_prices)
                await self.monitor_positions(positions)

            await asyncio.sleep(10)

    def stop(self):
        self._running = False
