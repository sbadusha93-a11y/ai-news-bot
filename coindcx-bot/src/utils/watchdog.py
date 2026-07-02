import asyncio
import os
import signal
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import psutil
from loguru import logger


class Watchdog:
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self._running = False
        self._health_checks: List[Callable] = []
        self._process = psutil.Process(os.getpid())
        self.health_status: Dict[str, Any] = {
            "status": "initializing",
            "uptime": 0,
            "cpu_percent": 0,
            "memory_percent": 0,
            "memory_mb": 0,
            "threads": 0,
            "last_check": datetime.now().isoformat(),
        }
        self._start_time = datetime.now()

    def add_health_check(self, check_fn: Callable):
        self._health_checks.append(check_fn)

    async def start(self):
        self._running = True
        self.health_status["status"] = "running"
        logger.info("Watchdog started")

        while self._running:
            await self._check_health()
            await asyncio.sleep(self.check_interval)

    async def _check_health(self):
        try:
            self._process.cpu_percent(interval=0.1)
            mem_info = self._process.memory_info()
            uptime = (datetime.now() - self._start_time).total_seconds()

            self.health_status.update({
                "uptime": uptime,
                "cpu_percent": self._process.cpu_percent(),
                "memory_percent": self._process.memory_percent(),
                "memory_mb": mem_info.rss / 1024 / 1024,
                "threads": self._process.num_threads(),
                "last_check": datetime.now().isoformat(),
            })

            for check in self._health_checks:
                try:
                    result = await check() if asyncio.iscoroutinefunction(check) else check()
                    if result is False:
                        logger.warning(f"Health check failed: {check.__name__}")
                except Exception as e:
                    logger.error(f"Health check error {check.__name__}: {e}")

        except Exception as e:
            logger.error(f"Watchdog health check failed: {e}")

    def get_status(self) -> Dict:
        return self.health_status

    async def stop(self):
        self._running = False
        logger.info("Watchdog stopped")
