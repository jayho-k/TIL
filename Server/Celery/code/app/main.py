from fastapi import FastAPI
from app.container import Container
from app.api.endpoints import router as user_router
from app.core.database import engine, Base

app = FastAPI()

container = Container()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Create tables for tutorial purposes
        await conn.run_sync(Base.metadata.create_all)

app.include_router(user_router)
