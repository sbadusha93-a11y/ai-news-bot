import json
import time
from typing import Any, Dict, Optional

import redis.asyncio as redis
from loguru import logger

from src.config import settings


class DataCache:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._local_cache: Dict[str, Dict] = {}
        self._local_ttl: Dict[str, float] = {}
        self._default_ttl = 300

    async def _get_redis(self) -> Optional[redis.Redis]:
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    settings.redis_url, decode_responses=True
                )
                await self._redis.ping()
            except Exception:
                logger.warning("Redis unavailable, using local cache")
                self._redis = None
        return self._redis

    async def get(self, key: str, default: Any = None) -> Any:
        r = await self._get_redis()
        if r:
            try:
                data = await r.get(key)
                if data:
                    return json.loads(data)
            except Exception:
                pass

        if key in self._local_cache:
            expiry = self._local_ttl.get(key, 0)
            if time.time() < expiry:
                return self._local_cache[key]
            else:
                self._local_cache.pop(key, None)
                self._local_ttl.pop(key, None)

        return default

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        if ttl is None:
            ttl = self._default_ttl

        r = await self._get_redis()
        if r:
            try:
                await r.setex(key, ttl, json.dumps(value, default=str))
                return True
            except Exception:
                pass

        self._local_cache[key] = value
        self._local_ttl[key] = time.time() + ttl
        return True

    async def delete(self, key: str):
        r = await self._get_redis()
        if r:
            try:
                await r.delete(key)
            except Exception:
                pass
        self._local_cache.pop(key, None)
        self._local_ttl.pop(key, None)

    async def exists(self, key: str) -> bool:
        r = await self._get_redis()
        if r:
            try:
                return bool(await r.exists(key))
            except Exception:
                pass
        return key in self._local_cache

    async def flush(self):
        r = await self._get_redis()
        if r:
            try:
                await r.flushdb()
            except Exception:
                pass
        self._local_cache.clear()
        self._local_ttl.clear()

    async def close(self):
        if self._redis:
            await self._redis.close()
