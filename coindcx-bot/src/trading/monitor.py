import asyncio
from typing import Callable, Dict, Optional

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

    async def monitor_positions(self, positions: Dict[str, Dict]):
        if not positions:
            return

        prices = await self._fetch_futures_prices(positions)
        if not prices:
            return

        for symbol, position in list(positions.items()):
            try:
                current_price = prices.get(symbol)
                if current_price is None or current_price == 0:
                    continue

                self.update_trailing_stops(position, current_price)

                action = self._evaluate_exit(position, current_price)
                if action:
                    logger.info(f"Exit signal for {symbol}: {action['reason']}")
                    if self.on_close:
                        await self.on_close(symbol, current_price, action["reason"])

            except Exception as e:
                logger.error(f"Error monitoring {symbol}: {e}")

    async def _fetch_futures_prices(self, positions: Dict[str, Dict]) -> Dict[str, float]:
        async def fetch_one(symbol: str) -> tuple:
            try:
                ticker = await self.exchange.fetch_ticker(symbol)
                if ticker:
                    price = ticker.get("last", 0)
                    if price != 0:
                        return symbol, price
            except Exception as e:
                logger.debug(f"Failed to fetch futures ticker for {symbol}: {e}")
            return symbol, None

        results = await asyncio.gather(*[fetch_one(s) for s in positions], return_exceptions=True)
        return {s: p for s, p in results if p is not None and not isinstance(p, Exception)}

    def _evaluate_exit(
        self, position: Dict, price: float
    ) -> Optional[Dict]:
        direction = position["side"]
        sl = position["stop_loss"]
        tp1 = position.get("take_profit_1", 0)
        tp2 = position.get("take_profit_2", 0)
        tp3 = position.get("take_profit_3", 0)

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

        trailing = position.get("trailing_stop_price")
        be = position.get("break_even_price")

        if trailing is not None or be is not None:
            exit_prices = []
            if trailing is not None:
                exit_prices.append(("trailing_stop", trailing))
            if be is not None:
                exit_prices.append(("break_even", be))

            for reason_name, exit_level in exit_prices:
                if (direction == "long" and price <= exit_level) or \
                   (direction == "short" and price >= exit_level):
                    return {"reason": reason_name}

        return None

    def update_trailing_stops(
        self, position: Dict, current_price: float
    ):
        direction = position["side"]
        entry = position["entry_price"]

        if direction == "long":
            if current_price > position.get("highest_price", entry):
                position["highest_price"] = current_price
        else:
            if current_price < position.get("lowest_price", entry):
                position["lowest_price"] = current_price

        sl = position["stop_loss"]
        atr = abs(current_price - sl) if sl != entry else 0

        atr_percent = current_price * 0.02
        vol_mult = atr / atr_percent if atr_percent > 0 else 1.0
        vol_mult = max(0.3, min(3.0, vol_mult))

        new_sl, trail_activated = self.position_sizer.calculate_trailing_stop(
            current_price, entry, abs(current_price - sl), direction,
            position.get("highest_price"), position.get("lowest_price"),
            volatility_mult=vol_mult,
        )
        if trail_activated:
            position["trailing_stop_price"] = new_sl

        be_price, be_activated = self.position_sizer.calculate_break_even_stop(
            current_price, entry, direction,
            volatility_mult=vol_mult,
        )
        if be_activated:
            position["break_even_price"] = be_price
