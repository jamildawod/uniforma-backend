from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic
from typing import Any

from redis.asyncio import Redis

from app.core.config import Settings


@dataclass(slots=True)
class CacheEntry:
    value: str
    expires_at: float


class CacheService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True) if settings.redis_url else None
        self._memory_cache: dict[str, CacheEntry] = {}

    async def get_json(self, key: str) -> Any | None:
        if self.redis is not None:
            payload = await self.redis.get(key)
            return json.loads(payload) if payload is not None else None
        entry = self._memory_cache.get(key)
        if entry is None or entry.expires_at < monotonic():
            self._memory_cache.pop(key, None)
            return None
        return json.loads(entry.value)

    async def get_version(self, namespace: str) -> int:
        version_key = f"{namespace}:version"
        if self.redis is not None:
            value = await self.redis.get(version_key)
            if not value:
                await self.redis.set(version_key, 1)
                return 1
            return int(value)
        entry = self._memory_cache.get(version_key)
        if entry is None or entry.expires_at < monotonic():
            self._memory_cache[version_key] = CacheEntry(value="1", expires_at=float("inf"))
            return 1
        return int(entry.value)

    async def bump_version(self, namespace: str) -> int:
        version_key = f"{namespace}:version"
        if self.redis is not None:
            return int(await self.redis.incr(version_key))
        current = await self.get_version(namespace)
        next_value = current + 1
        self._memory_cache[version_key] = CacheEntry(value=str(next_value), expires_at=float("inf"))
        return next_value

    async def set_json(self, key: str, value: Any, ttl: int | None = None) -> None:
        encoded = json.dumps(value, default=str, ensure_ascii=False)
        ttl_seconds = ttl or self.settings.cache_ttl_seconds
        if self.redis is not None:
            await self.redis.set(key, encoded, ex=ttl_seconds)
            return
        self._memory_cache[key] = CacheEntry(value=encoded, expires_at=monotonic() + ttl_seconds)

    async def get_or_set_json(self, key: str, factory: Callable[[], Any], ttl: int | None = None) -> Any:
        cached = await self.get_json(key)
        if cached is not None:
            return cached
        value = await factory()
        await self.set_json(key, value, ttl=ttl)
        return value

    async def invalidate_prefix(self, prefix: str) -> None:
        if self.redis is not None:
            cursor = 0
            pattern = f"{prefix}*"
            while True:
                cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=200)
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
            return
        for key in list(self._memory_cache.keys()):
            if key.startswith(prefix):
                self._memory_cache.pop(key, None)
