from typing import cast

from fastapi import Request
from redis.asyncio import Redis

from benchflow.application.ports.bench_lock import BenchLock
from benchflow.config import Settings
from benchflow.infrastructure.redis.bench_lock import RedisBenchLock


def get_bench_lock(
        request: Request,
) -> BenchLock:
    """Provide a Redis-backed bench lock."""

    redis = cast(
        Redis,
        request.app.state.redis,
    )
    settings = cast(
        Settings,
        request.app.state.settings,
    )

    return RedisBenchLock(
        redis=redis,
        ttl_seconds=settings.bench_lock_ttl_seconds,
    )
