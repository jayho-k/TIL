import pytest

from load_tests.clients import consume_sse


class ByteResponse:
    def iter_lines(self):
        yield b"event: stream.completed"
        yield b'data: {"ok":true}'
        yield b""


def test_consumer_accepts_bytes_from_requests() -> None:
    stats = consume_sse(ByteResponse())

    assert stats.events == 1
    assert stats.terminal_event == "stream.completed"
    assert stats.bytes_read > 0


def test_timings_include_header_wait_and_full_body(monkeypatch):
    clock = iter([11.0, 11.5, 12.0])
    monkeypatch.setattr("load_tests.clients.perf_counter", lambda: next(clock))

    class Response:
        def iter_lines(self):
            yield "event: stream.started"
            yield 'data: {}'
            yield ""
            yield "event: message.delta"
            yield 'data: {"data":{"text":"hello"}}'
            yield ""
            yield "event: stream.completed"
            yield 'data: {}'
            yield ""

    stats = consume_sse(Response(), started_at=10.0)
    assert stats.first_event_ms == pytest.approx(1000)
    assert stats.first_token_ms == pytest.approx(1500)
    assert stats.duration_ms == pytest.approx(2000)
