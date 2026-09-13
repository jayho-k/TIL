from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ollama_base_url: str
    ollama_model: str
    ollama_api_key: str = "ollama"
    ollama_reasoning_effort_enabled: bool = True
    redis_url: str = "redis://localhost:6379"
    data_dir: Path = Field(default=Path("data/runs"))
    agent_api_url: str = "http://localhost:8000"
