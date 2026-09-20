from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from redis.asyncio import Redis
from sqlalchemy import text

from app.agents.factory import create_chat_agent
from app.agents.model import create_model
from app.agents.source import LangGraphEventSource
from app.api.routes import router
from app.config import Settings
from app.domain.models import Transport
from app.observability.metrics import Metrics
from app.persistence.database import create_database
from app.persistence.repository import SqlAlchemyRunRepository
from app.service.chat import ChatStreamService
from app.service.limits import ConcurrencyLimiter
from app.streaming.adapters import EventSourceResponseAdapter
from app.streaming.projector import StreamEventProjector


def _set_adapters(app: FastAPI, heartbeat: float, send_timeout: float) -> None:
    app.state.response_adapters = {
        Transport.EVENT_SOURCE_RESPONSE: EventSourceResponseAdapter(
            heartbeat_seconds=heartbeat,
            send_timeout_seconds=send_timeout,
        ),
    }


@asynccontextmanager
async def production_lifespan(app: FastAPI):
    settings = Settings()
    engine, session_factory = create_database(settings)
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    async with AsyncRedisSaver.from_conn_string(settings.redis_url) as checkpointer:
        await redis.ping()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        await checkpointer.asetup()
        model = create_model(settings)
        graph = create_chat_agent(model, checkpointer)
        repository = SqlAlchemyRunRepository(
            session_factory,
            max_error_message_length=settings.max_error_message_length,
        )
        app.state.chat_service = ChatStreamService(
            source=LangGraphEventSource(graph),
            projector=StreamEventProjector(),
            repository=repository,
            limiter=ConcurrencyLimiter(
                capacity=settings.max_agent_runs,
                timeout_seconds=settings.permit_timeout_seconds,
            ),
            model_name=settings.ollama_model,
            timeout_seconds=settings.agent_timeout_seconds,
            token_batch_max_chars=settings.token_batch_max_chars,
            token_batch_max_delay_seconds=settings.token_batch_max_delay_seconds,
            metrics=app.state.metrics,
        )
        app.state.connection_limiter = ConcurrencyLimiter(
            capacity=settings.max_sse_connections,
            timeout_seconds=settings.permit_timeout_seconds,
        )
        app.state.readiness = lambda: True
        _set_adapters(app, settings.heartbeat_seconds, settings.send_timeout_seconds)
        try:
            yield
        finally:
            app.state.readiness = lambda: False
            await redis.aclose()
            await engine.dispose()


def create_app(
    *,
    service=None,
    readiness: Callable[[], object] | None = None,
    heartbeat_seconds: float = 15,
    send_timeout_seconds: float = 30,
    production: bool = False,
    connection_limiter: ConcurrencyLimiter | None = None,
) -> FastAPI:
    app = FastAPI(
        title="DeepAgent EventSource Streaming",
        version="0.1.0",
        lifespan=production_lifespan if production else None,
    )
    app.state.chat_service = service
    app.state.metrics = Metrics()
    app.state.metrics_registry = app.state.metrics.registry
    app.state.readiness = readiness or (lambda: service is not None)
    app.state.connection_limiter = connection_limiter or ConcurrencyLimiter(
        capacity=30,
        timeout_seconds=5,
    )
    _set_adapters(app, heartbeat_seconds, send_timeout_seconds)
    app.include_router(router)
    return app


app = create_app(production=True)
