import os
from time import perf_counter
from uuid import uuid4

from locust import HttpUser, between, task

from load_tests.clients import consume_sse

TRANSPORT = os.getenv("STREAM_TRANSPORT", "stream")


class ChatUser(HttpUser):
    wait_time = between(0.8, 1.2)

    @task(84)
    def normal(self):
        self._stream()

    @task(10)
    def slow_consumer(self):
        self._stream(slow_delay=0.05)

    @task(6)
    def early_disconnect(self):
        started = perf_counter()
        with self.client.post(
            f"/v1/chat/{TRANSPORT}",
            json={"thread_id": str(uuid4()), "message": "짧게 인사해줘"},
            stream=True,
            catch_response=True,
            name=f"/v1/chat/{TRANSPORT}:early-disconnect",
        ) as response:
            try:
                next(response.iter_lines(), None)
            finally:
                response.request_meta["response_time"] = (perf_counter() - started) * 1000
                response.close()

    def _stream(self, *, slow_delay: float = 0.0):
        started = perf_counter()
        with self.client.post(
            f"/v1/chat/{TRANSPORT}",
            json={"thread_id": str(uuid4()), "message": "짧게 인사해줘"},
            stream=True,
            catch_response=True,
            name=f"/v1/chat/{TRANSPORT}",
        ) as response:
            try:
                if response.status_code != 200:
                    response.failure(f"HTTP {response.status_code}")
                    return
                stats = consume_sse(response, slow_delay=slow_delay, started_at=started)
                response.request_meta["response_length"] = stats.bytes_read
                for name, value in (("first-event", stats.first_event_ms),
                                    ("first-token", stats.first_token_ms)):
                    if value is not None:
                        self.environment.events.request.fire(
                            request_type="SSE", name=f"{TRANSPORT}:{name}",
                            response_time=value, response_length=0, exception=None,
                        )
                if stats.terminal_event != "stream.completed":
                    response.failure(f"terminal={stats.terminal_event}")
            except Exception as exc:
                response.failure(type(exc).__name__)
            finally:
                response.request_meta["response_time"] = (perf_counter() - started) * 1000
                response.close()
