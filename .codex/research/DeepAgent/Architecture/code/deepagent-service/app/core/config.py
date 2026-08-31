from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseModel):
    postgres_url: str = "postgresql+asyncpg://app:app@localhost:5432/app"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DEEPAGENT_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = "Deep Agent Service"
    model_name: str = "openai:gpt-5-mini"
    storage: StorageSettings = StorageSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()

