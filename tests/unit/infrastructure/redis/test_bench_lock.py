from unittest.mock import AsyncMock
from uuid import uuid4

from benchflow.infrastructure.redis.bench_lock import RedisBenchLock


async def test_acquire_sets_expiring_lock() -> None:
    """Acquire a bench lock with an expiration."""

    redis = AsyncMock()
    redis.set.return_value = True

    lock = RedisBenchLock(
        redis=redis,
        ttl_seconds=30,
    )

    bench_id = uuid4()
    run_id = uuid4()

    acquired = await lock.acquire(
        bench_id,
        run_id,
    )

    assert acquired is True

    redis.set.assert_awaited_once_with(
        f"bench:{bench_id}:lock",
        str(run_id),
        nx=True,
        ex=30,
    )


async def test_acquire_returns_false_when_locked() -> None:
    """Reject acquisition when the bench is already locked."""

    redis = AsyncMock()
    redis.set.return_value = None

    lock = RedisBenchLock(
        redis=redis,
        ttl_seconds=30,
    )

    acquired = await lock.acquire(
        uuid4(),
        uuid4(),
    )

    assert acquired is False


async def test_release_checks_lock_owner() -> None:
    """Release a bench lock using the run as its owner."""

    redis = AsyncMock()

    lock = RedisBenchLock(
        redis=redis,
        ttl_seconds=30,
    )

    bench_id = uuid4()
    run_id = uuid4()

    await lock.release(
        bench_id,
        run_id,
    )

    redis.eval.assert_awaited_once()

    _, key_count, key, owner = redis.eval.await_args.args

    assert key_count == 1
    assert key == f"bench:{bench_id}:lock"
    assert owner == str(run_id)
