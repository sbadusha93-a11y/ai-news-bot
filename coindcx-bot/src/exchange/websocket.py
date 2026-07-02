import asyncio
import json
from typing import Callable, Dict, List, Optional

import websockets
from loguru import logger


class CoinDCXWebSocket:
    def __init__(self):
        self.base_url = "wss://stream.coindcx.com"
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._running = False
        self._callbacks: Dict[str, List[Callable]] = {}
        self._reconnect_delay = 5
        self._max_reconnect_delay = 300
        self._connect_attempts = 0
        self._max_connect_attempts = 5

    async def connect(self):
        self._connect_attempts += 1
        if self._connect_attempts > self._max_connect_attempts:
            logger.warning(f"WebSocket max reconnect attempts ({self._max_connect_attempts}) reached, giving up")
            self._running = False
            return

        try:
            self._ws = await websockets.connect(
                f"{self.base_url}/market/ws",
                ping_interval=30,
                ping_timeout=10,
                open_timeout=10,
            )
            self._reconnect_delay = 5
            self._connect_attempts = 0
            logger.info("WebSocket connected")
        except Exception as e:
            logger.debug(f"WebSocket connection failed (attempt {self._connect_attempts}): {e}")
            if self._running:
                await self._reconnect()

    async def _reconnect(self):
        self._reconnect_delay = min(self._reconnect_delay * 2, self._max_reconnect_delay)
        logger.debug(f"WebSocket reconnecting in {self._reconnect_delay}s...")
        await asyncio.sleep(self._reconnect_delay)
        await self.connect()

    async def subscribe(self, channels: List[Dict]):
        if self._ws:
            payload = {"type": "subscribe", "channels": channels}
            await self._ws.send(json.dumps(payload))

    async def subscribe_ticker(self, symbols: List[str]):
        channels = [
            {"name": "ticker", "pairs": [s.replace("_", "-") for s in symbols]}
        ]
        await self.subscribe(channels)

    async def subscribe_ohlcv(self, symbols: List[str], timeframe: str = "4h"):
        channels = [
            {
                "name": f"ohlcv-{timeframe}",
                "pairs": [s.replace("_", "-") for s in symbols],
            }
        ]
        await self.subscribe(channels)

    async def subscribe_trades(self, symbols: List[str]):
        channels = [
            {"name": "trades", "pairs": [s.replace("_", "-") for s in symbols]}
        ]
        await self.subscribe(channels)

    async def subscribe_orderbook(self, symbols: List[str]):
        channels = [
            {
                "name": "depth",
                "pairs": [s.replace("_", "-") for s in symbols],
            }
        ]
        await self.subscribe(channels)

    def on_message(self, channel: str, callback: Callable):
        if channel not in self._callbacks:
            self._callbacks[channel] = []
        self._callbacks[channel].append(callback)

    async def _handle_message(self, message: str):
        try:
            data = json.loads(message)
            channel = data.get("channel", "")
            if channel in self._callbacks:
                for cb in self._callbacks[channel]:
                    await cb(data)
        except Exception as e:
            logger.error(f"WebSocket message handler error: {e}")

    async def start(self):
        self._running = True
        while self._running:
            try:
                if not self._ws:
                    await self.connect()
                if not self._ws:
                    await asyncio.sleep(30)
                    continue
                async for message in self._ws:
                    if not self._running:
                        break
                    await self._handle_message(message)
            except websockets.ConnectionClosed:
                logger.debug("WebSocket connection closed")
                if self._running:
                    await self._reconnect()
            except Exception as e:
                logger.debug(f"WebSocket error: {e}")
                if self._running and self._connect_attempts <= self._max_connect_attempts:
                    await self._reconnect()
                else:
                    await asyncio.sleep(60)

    async def stop(self):
        self._running = False
        if self._ws:
            await self._ws.close()
