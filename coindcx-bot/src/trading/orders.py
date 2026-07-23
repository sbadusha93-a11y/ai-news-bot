import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from loguru import logger


class OrderStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    OCO = "oco"


class SmartOrderManager:
    def __init__(
        self,
        create_order_fn: Callable,
        cancel_order_fn: Callable,
        fetch_order_fn: Optional[Callable] = None,
        fill_timeout: float = 30.0,
        poll_interval: float = 2.0,
        max_cancel_attempts: int = 3,
    ):
        self._create = create_order_fn
        self._cancel = cancel_order_fn
        self._fetch = fetch_order_fn
        self.fill_timeout = fill_timeout
        self.poll_interval = poll_interval
        self.max_cancel_attempts = max_cancel_attempts

    async def place_and_confirm(
        self,
        symbol: str,
        order_type: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        logger.info(f"Placing {order_type} {side} {quantity} {symbol} @ {price or 'market'}")

        timeout = timeout or self.fill_timeout
        order = await self._create(symbol, order_type, side, quantity, price, stop_price)
        if not order:
            return {"status": OrderStatus.REJECTED.value, "filled_quantity": 0.0}
        order_id = order.get("id", "")
        if not order_id:
            return {"status": OrderStatus.FILLED.value, "filled_quantity": quantity, "order": order}

        if self._fetch is None:
            return {"status": OrderStatus.FILLED.value, "filled_quantity": quantity, "order": order}

        result = await self._poll_fill(order_id, symbol, timeout)
        return result

    async def _poll_fill(
        self, order_id: str, symbol: str, timeout: float
    ) -> Dict[str, Any]:
        deadline = datetime.now(timezone.utc).timestamp() + timeout
        last_remaining = None

        while datetime.now(timezone.utc).timestamp() < deadline:
            try:
                status = await self._fetch(order_id, symbol)
                if not status:
                    await asyncio.sleep(self.poll_interval)
                    continue

                remaining = float(status.get("remaining_quantity", status.get("pending_quantity", 0)))
                filled = float(status.get("filled_quantity", 0))
                order_status = status.get("status", "").lower()

                if order_status in ("filled", "closed"):
                    return {
                        "status": OrderStatus.FILLED.value,
                        "filled_quantity": filled,
                        "remaining": 0.0,
                        "avg_price": float(status.get("price_per_unit", status.get("avg_price", 0))),
                        "order": status,
                    }

                if order_status in ("cancelled", "rejected", "expired"):
                    return {
                        "status": OrderStatus.CANCELLED.value if order_status == "cancelled" else OrderStatus.REJECTED.value,
                        "filled_quantity": filled,
                        "remaining": remaining,
                        "order": status,
                    }

                if remaining > 0 and filled > 0:
                    logger.info(f"Order {order_id} partial fill: {filled} filled, {remaining} remaining")

                if last_remaining is not None and last_remaining == remaining and remaining > 0:
                    logger.info(f"Order {order_id} stale ({remaining} unfilled) — cancel and retry")
                    cancel_ok = await self._cancel_with_retry(order_id, symbol)
                    if cancel_ok:
                        return {
                            "status": OrderStatus.CANCELLED.value,
                            "filled_quantity": filled,
                            "remaining": remaining,
                            "order": status,
                        }
                last_remaining = remaining

            except Exception as e:
                logger.warning(f"Order poll error {order_id}: {e}")

            await asyncio.sleep(self.poll_interval)

        logger.warning(f"Order {order_id} fill timeout ({timeout}s)")
        await self._cancel_with_retry(order_id, symbol)
        return {
            "status": OrderStatus.EXPIRED.value,
            "filled_quantity": 0.0,
            "remaining": 0.0,
        }

    async def _cancel_with_retry(self, order_id: str, symbol: str) -> bool:
        for attempt in range(self.max_cancel_attempts):
            try:
                result = await self._cancel(symbol, order_id)
                if result:
                    return True
            except Exception as e:
                logger.warning(f"Cancel attempt {attempt + 1} failed for {order_id}: {e}")
            await asyncio.sleep(0.5)
        logger.error(f"Failed to cancel order {order_id} after {self.max_cancel_attempts} attempts")
        return False

    async def place_oco(
        self,
        symbol: str,
        side: str,
        quantity: float,
        take_profit_price: float,
        stop_loss_price: float,
    ) -> Dict[str, Any]:
        close_side = "sell" if side == "long" else "buy"
        tp_side = close_side
        sl_side = "buy" if side == "long" else "sell"

        tp_order = await self._create(
            symbol, "limit", tp_side, quantity, take_profit_price, None
        )
        sl_order = await self._create(
            symbol, "stop_market", sl_side, quantity, None, stop_loss_price
        )

        return {
            "take_profit": {
                "order_id": tp_order.get("id", "") if tp_order else None,
                "price": take_profit_price,
                "status": "placed",
            },
            "stop_loss": {
                "order_id": sl_order.get("id", "") if sl_order else None,
                "price": stop_loss_price,
                "status": "placed",
            },
        }

    async def modify_order(
        self,
        order_id: str,
        symbol: str,
        new_price: Optional[float] = None,
        new_quantity: Optional[float] = None,
        new_stop_price: Optional[float] = None,
    ) -> bool:
        logger.info(f"Modifying order {order_id} for {symbol}")
        try:
            await self._cancel(order_id, symbol)
            return True
        except Exception as e:
            logger.error(f"Failed to modify order {order_id}: {e}")
            return False

    def estimate_slippage(
        self,
        side: str,
        quantity: float,
        price: float,
        volume: float,
        volatility_pct: float = 0.001,
    ) -> float:
        if volume <= 0 or price <= 0:
            return price * (1 + volatility_pct if side == "buy" else 1 - volatility_pct)
        order_value = quantity * price
        market_impact = order_value / volume if volume > 0 else 0
        slippage_pct = volatility_pct + min(market_impact * 0.5, 0.01)
        if side in ("buy", "long"):
            return round(price * (1 + slippage_pct), 8)
        else:
            return round(price * (1 - slippage_pct), 8)
