import asyncio

from app.api.main import create_app
from app.domain.events import PublicEventType, StreamEvent


class FakeLoadService:
    async def stream(self, command):
        yield StreamEvent.create(
            event_type=PublicEventType.STREAM_STARTED,
            run_id=command.run_id,
            thread_id=command.thread_id,
            sequence=0,
            data={"transport": command.transport.value},
        )
        for sequence in range(1, 11):
            await asyncio.sleep(0.02)
            yield StreamEvent.create(
                event_type=PublicEventType.MESSAGE_DELTA,
                run_id=command.run_id,
                thread_id=command.thread_id,
                sequence=sequence,
                data={"text": "token"},
            )
        yield StreamEvent.create(
            event_type=PublicEventType.STREAM_COMPLETED,
            run_id=command.run_id,
            thread_id=command.thread_id,
            sequence=11,
            data={"latency_ms": 200, "output_chars": 50},
        )


app = create_app(service=FakeLoadService(), readiness=lambda: True)
