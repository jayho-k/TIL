from app.config import Settings


def test_settings_loads_ollama_and_redis(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("OLLAMA_API_KEY", "ollama")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")

    settings = Settings(_env_file=None)

    assert settings.ollama_base_url == "http://ollama.test/v1"
    assert settings.ollama_model == "test-model"
    assert settings.redis_url == "redis://localhost:6379"
