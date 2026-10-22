import pytest

from tac_two.adapters.settings import Settings


def test_settings_read_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    assert Settings().database_url == "sqlite+aiosqlite:///:memory:"
