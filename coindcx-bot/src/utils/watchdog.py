import asyncio
import os
import signal
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

import psutil
from loguru import logger


class Watchdog:
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self._running = False
        self._health_checks: List[Callable] = []
        self._recovery_actions: Dict[str, Callable] = {}
        self._consecutive_failures: Dict[str, int] = {}
        self._process = psutil.Process(os.getpid())
        self.health_status: Dict[str, Any] = {
            "status": "initializing",
            "uptime": 0,
            "cpu_percent": 0,
            "memory_percent": 0,
            "memory_mb": 0,
            "threads": 0,
            "last_check": datetime.now(timezone.utc).isoformat(),
        }
        self._start_time = datetime.now(timezone.utc)

    def add_health_check(self, check_fn: Callable):
        self._health_checks.append(check_fn)

    def add_recovery_action(self, name: str, action: Callable):
        self._recovery_actions[name] = action
        self._consecutive_failures[name] = 0

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
            uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()

            self.health_status.update({
                "uptime": uptime,
                "cpu_percent": self._process.cpu_percent(),
                "memory_percent": self._process.memory_percent(),
                "memory_mb": mem_info.rss / 1024 / 1024,
                "threads": self._process.num_threads(),
                "last_check": datetime.now(timezone.utc).isoformat(),
            })

            if self.health_status["memory_mb"] > 2000:
                logger.warning(f"High memory usage: {self.health_status['memory_mb']:.0f}MB")

            for check in self._health_checks:
                try:
                    result = await check() if asyncio.iscoroutinefunction(check) else check()
                    if result is False:
                        logger.warning(f"Health check failed: {check.__name__}")
                except Exception as e:
                    logger.error(f"Health check error {check.__name__}: {e}")

        except Exception as e:
            logger.error(f"Watchdog health check failed: {e}")

    async def recover_from(self, error_name: str, error: Exception):
        full_tb = traceback.format_exc()
        logger.error(f"Recovery triggered for '{error_name}': {error}\n{full_tb}")

        self._consecutive_failures[error_name] = self._consecutive_failures.get(error_name, 0) + 1
        max_failures = 3

        if self._consecutive_failures[error_name] > max_failures:
            logger.warning(f"Too many consecutive failures for '{error_name}' ({self._consecutive_failures[error_name]}). Sending shutdown signal.")
            self._running = False
            asyncio.get_event_loop().stop()
            return

        if error_name in self._recovery_actions:
            try:
                await self._recovery_actions[error_name]()
                logger.info(f"Recovery action for '{error_name}' completed")
                self._consecutive_failures[error_name] = 0
            except Exception as recovery_error:
                logger.error(f"Recovery action for '{error_name}' failed: {recovery_error}")

        await asyncio.sleep(5)

    async def try_fix_and_restart(self, component: str, fix_func: Callable):
        logger.info(f"Attempting auto-recovery for: {component}")
        try:
            result = await fix_func() if asyncio.iscoroutinefunction(fix_func) else fix_func()
            if result:
                logger.success(f"Auto-recovery successful for: {component}")
            else:
                logger.warning(f"Auto-recovery failed for: {component}")
            return result
        except Exception as e:
            logger.error(f"Auto-recovery error for {component}: {e}")
            return False

    def get_status(self) -> Dict:
        return self.health_status

    async def stop(self):
        self._running = False
        logger.info("Watchdog stopped")
