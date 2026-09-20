import pytest

from app.service.limits import CapacityExceeded, ConcurrencyLimiter


@pytest.mark.asyncio
async def test_limiter_releases_permit_after_context() -> None:
    limiter = ConcurrencyLimiter(capacity=1, timeout_seconds=0.01)

    async with limiter.slot():
        assert limiter.active == 1

    assert limiter.active == 0


@pytest.mark.asyncio
async def test_limiter_fails_when_capacity_is_exhausted() -> None:
    limiter = ConcurrencyLimiter(capacity=1, timeout_seconds=0.01)

    async with limiter.slot():
        with pytest.raises(CapacityExceeded):
            async with limiter.slot():
                raise AssertionError("unreachable")


@pytest.mark.asyncio
async def test_limiter_can_admit_before_response_and_release_later() -> None:
    limiter = ConcurrencyLimiter(capacity=1, timeout_seconds=0.01)

    await limiter.acquire()
    assert limiter.active == 1
    with pytest.raises(CapacityExceeded):
        await limiter.acquire()
    limiter.release()

    assert limiter.active == 0
