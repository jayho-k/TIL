from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PositiveInt = Annotated[int, Field(gt=0)]
PositiveFloat = Annotated[float, Field(gt=0)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_dsn: str
    redis_url: str = "redis://localhost:6379"

    ollama_base_url: str
    ollama_model: str
    ollama_api_key: str = "ollama"
    ollama_reasoning_effort_enabled: bool = True

    max_sse_connections: PositiveInt = 30
    max_agent_runs: PositiveInt = 10
    heartbeat_seconds: PositiveFloat = 15.0
    send_timeout_seconds: PositiveFloat = 30.0
    agent_timeout_seconds: PositiveFloat = 600.0
    permit_timeout_seconds: PositiveFloat = 5.0
    token_batch_max_chars: PositiveInt = 128
    token_batch_max_delay_seconds: PositiveFloat = 0.02

    db_pool_size: PositiveInt = 20
    db_max_overflow: int = Field(default=20, ge=0)
    db_pool_timeout_seconds: PositiveFloat = 5.0
    max_thread_id_length: PositiveInt = 128
    max_message_length: PositiveInt = 20_000
    max_error_message_length: PositiveInt = 1_000
