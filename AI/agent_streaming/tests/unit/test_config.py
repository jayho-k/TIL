import pytest
from pydantic import ValidationError

from app.config import Settings


def configure_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_DSN", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")


def test_settings_have_safe_stream_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    configure_required(monkeypatch)

    settings = Settings(_env_file=None)

    assert settings.redis_url == "redis://localhost:6379"
    assert settings.max_sse_connections == 30
    assert settings.max_agent_runs == 10
    assert settings.heartbeat_seconds == 15.0
    assert settings.send_timeout_seconds == 30.0
    assert settings.agent_timeout_seconds == 600.0
    assert settings.permit_timeout_seconds == 5.0


def test_settings_require_external_services(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("POSTGRES_DSN", "OLLAMA_BASE_URL", "OLLAMA_MODEL"):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_reject_non_positive_limits(monkeypatch: pytest.MonkeyPatch) -> None:
    configure_required(monkeypatch)
    monkeypatch.setenv("MAX_AGENT_RUNS", "0")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
