from collections.abc import Callable
from time import monotonic


class TokenBatcher:
    def __init__(
        self,
        *,
        max_chars: int,
        max_delay_seconds: float,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._max_chars = max_chars
        self._max_delay_seconds = max_delay_seconds
        self._clock = clock
        self._parts: list[str] = []
        self._length = 0
        self._started_at: float | None = None

    def add(self, text: str) -> None:
        if not text:
            return
        if self._started_at is None:
            self._started_at = self._clock()
        self._parts.append(text)
        self._length += len(text)

    def should_flush(self) -> bool:
        if not self._parts or self._started_at is None:
            return False
        return (
            self._length >= self._max_chars
            or self._clock() - self._started_at >= self._max_delay_seconds
        )

    def flush(self) -> str:
        value = "".join(self._parts)
        self._parts.clear()
        self._length = 0
        self._started_at = None
        return value

    @property
    def remaining_seconds(self) -> float | None:
        if self._started_at is None:
            return None
        return max(0.0, self._max_delay_seconds - (self._clock() - self._started_at))

    @property
    def pending(self) -> bool:
        return bool(self._parts)
