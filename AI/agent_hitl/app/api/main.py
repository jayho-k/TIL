from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from redis.asyncio import Redis

from app.agents.document import create_document_agent
from app.agents.model import create_model
from app.api.routes import router
from app.config import Settings
from app.runs.repository import RedisRunRepository
from app.service.runner import AgentRunner
from app.storage.files import LocalRunFileStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    repository = RedisRunRepository(redis)
    files = LocalRunFileStore(settings.data_dir)
    async with AsyncRedisSaver.from_conn_string(settings.redis_url) as checkpointer:
        await checkpointer.asetup()
        model = create_model(settings)
        agent = create_document_agent(model, files, checkpointer)
        app.state.settings = settings
        app.state.repository = repository
        app.state.files = files
        app.state.runner = AgentRunner(agent, repository, files)
        yield
    await redis.aclose()


app = FastAPI(title="DeepAgent HITL PoC", lifespan=lifespan)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
