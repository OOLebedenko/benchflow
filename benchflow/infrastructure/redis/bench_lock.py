from uuid import UUID

from redis.asyncio import Redis

from benchflow.application.ports.bench_lock import BenchLock

_RELEASE_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


class RedisBenchLock(BenchLock):
    """Coordinate exclusive bench access with Redis."""

    def __init__(
            self,
            redis: Redis,
            ttl_seconds: int,
    ) -> None:
        self._redis = redis
        self._ttl_seconds = ttl_seconds

    async def acquire(
            self,
            bench_id: UUID,
            run_id: UUID,
    ) -> bool:
        """Try to acquire an expiring bench lock."""

        result = await self._redis.set(
            self._key(bench_id),
            str(run_id),
            nx=True,
            ex=self._ttl_seconds,
        )

        return bool(result)

    async def release(
            self,
            bench_id: UUID,
            run_id: UUID,
    ) -> None:
        """Release the lock only when owned by the run."""

        await self._redis.eval(
            _RELEASE_SCRIPT,
            1,
            self._key(bench_id),
            str(run_id),
        )

    @staticmethod
    def _key(
            bench_id: UUID,
    ) -> str:
        return f"bench:{bench_id}:lock"
