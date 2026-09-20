from langchain_openai import ChatOpenAI

from app.config import Settings


def create_model(settings: Settings) -> ChatOpenAI:
    options: dict[str, object] = {
        "api_key": settings.ollama_api_key,
        "base_url": settings.ollama_base_url,
        "model": settings.ollama_model,
        "streaming": True,
        "timeout": settings.agent_timeout_seconds,
        "max_retries": 1,
    }
    if settings.ollama_reasoning_effort_enabled:
        options["reasoning_effort"] = "none"
    return ChatOpenAI(**options)  # type: ignore[arg-type]
