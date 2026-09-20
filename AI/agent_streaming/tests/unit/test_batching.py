from app.streaming.batching import TokenBatcher


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_batcher_flushes_by_size_and_resets() -> None:
    clock = Clock()
    batcher = TokenBatcher(max_chars=5, max_delay_seconds=0.02, clock=clock)

    batcher.add("abc")
    assert not batcher.should_flush()
    batcher.add("de")
    assert batcher.should_flush()
    assert batcher.flush() == "abcde"
    assert batcher.flush() == ""


def test_batcher_flushes_by_elapsed_time() -> None:
    clock = Clock()
    batcher = TokenBatcher(max_chars=100, max_delay_seconds=0.02, clock=clock)
    batcher.add("a")

    clock.now = 0.021

    assert batcher.should_flush()
    assert batcher.flush() == "a"
