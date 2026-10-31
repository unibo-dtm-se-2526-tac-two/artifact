import pytest

from tac_two.adapters.settings import Settings


def test_settings_read_database_url_and_secret_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    settings = Settings()
    assert settings.database_url == "sqlite+aiosqlite:///:memory:"
    assert settings.secret_key == "test-secret"
