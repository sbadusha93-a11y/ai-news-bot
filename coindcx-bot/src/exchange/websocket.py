import asyncio
import json
import random
from typing import Callable, Dict, List, Optional

import websockets
from loguru import logger


class CoinDCXWebSocket:
    def __init__(self):
        self.base_urls = [
            "wss://stream.coindcx.com",
        ]
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._running = False
        self._callbacks: Dict[str, List[Callable]] = {}
        self._reconnect_delay = 5
        self._max_reconnect_delay = 300
        self._connect_attempts = 0
        self._consecutive_failures = 0
        self._current_url_index = 0

    async def connect(self):
        self._connect_attempts += 1
        base_url = self.base_urls[self._current_url_index % len(self.base_urls)]
        for attempt in range(3):
            try:
                self._ws = await websockets.connect(
                    f"{base_url}/market/ws",
                    ping_interval=30,
                    ping_timeout=10,
                    open_timeout=15,
                    close_timeout=10,
                )
                self._reconnect_delay = 5
                self._connect_attempts = 0
                self._consecutive_failures = 0
                logger.info(f"WebSocket connected to {base_url}")
                return
            except Exception as e:
                self._consecutive_failures += 1
                if "503" in str(e) or "502" in str(e):
                    logger.warning(f"WebSocket server unavailable ({e}), retry {attempt+1}/3")
                    await asyncio.sleep(5 * (attempt + 1))
                else:
                    logger.debug(f"WebSocket connection failed (attempt {self._connect_attempts}): {e}")
                    break

        if self._running:
            self._ws = None
            self._current_url_index += 1
            asyncio.create_task(self._delayed_reconnect())

    async def _delayed_reconnect(self):
        jitter = random.uniform(0.5, 1.5)
        delay = min(self._reconnect_delay * jitter, self._max_reconnect_delay)
        self._reconnect_delay = min(self._reconnect_delay * 2, self._max_reconnect_delay)
        logger.debug(f"WebSocket reconnecting in {delay:.1f}s (attempt {self._connect_attempts})...")
        await asyncio.sleep(delay)
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
                    self._ws = None
                    asyncio.create_task(self._delayed_reconnect())
                    await asyncio.sleep(5)
            except Exception as e:
                logger.debug(f"WebSocket error: {e}")
                self._ws = None
                if self._running:
                    asyncio.create_task(self._delayed_reconnect())
                    await asyncio.sleep(60)

    async def stop(self):
        self._running = False
        if self._ws:
            await self._ws.close()
