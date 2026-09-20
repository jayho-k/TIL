import asyncio
from contextlib import asynccontextmanager


class CapacityExceeded(RuntimeError):
    pass


class ConcurrencyLimiter:
    def __init__(self, *, capacity: int, timeout_seconds: float) -> None:
        self._semaphore = asyncio.BoundedSemaphore(capacity)
        self._timeout_seconds = timeout_seconds
        self._active = 0

    @property
    def active(self) -> int:
        return self._active

    async def acquire(self) -> None:
        try:
            async with asyncio.timeout(self._timeout_seconds):
                await self._semaphore.acquire()
        except TimeoutError as exc:
            raise CapacityExceeded("concurrency capacity exhausted") from exc
        self._active += 1

    def release(self) -> None:
        self._active -= 1
        self._semaphore.release()

    @asynccontextmanager
    async def slot(self):
        await self.acquire()
        try:
            yield
        finally:
            self.release()
