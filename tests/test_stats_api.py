from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tac_two.adapters.database import create_engine, create_session_maker
from tac_two.adapters.match_repository import SqlMatchRepository
from tac_two.adapters.models import Base
from tac_two.api.app import app
from tac_two.api.dependencies import get_session
from tac_two.domain.ai.factory import Difficulty
from tac_two.domain.game.common import Player
from tac_two.domain.match import EndReason, GameMode, Match

START = datetime(2026, 11, 1, 10, 0, 0, tzinfo=timezone.utc)


@pytest_asyncio.fixture
async def session_maker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    database_url = f"sqlite+aiosqlite:///{(tmp_path / 'test.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("SECRET_KEY", "a-test-secret-key-that-is-long-enough")
    engine = create_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    maker = create_session_maker(engine)

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield maker
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def register_and_login(client: AsyncClient) -> tuple[str, UUID]:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "sofia@example.com",
            "password": "password123",
            "username": "sofia",
        },
    )
    user_id = UUID(response.json()["id"])
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "sofia@example.com", "password": "password123"},
    )
    return response.json()["access_token"], user_id


def make_match(
    user_id: UUID,
    winner: Player,
    mode: GameMode = GameMode.COMPUTER,
    difficulty: Difficulty | None = Difficulty.EASY,
) -> Match:
    return Match(
        id=uuid4(),
        mode=mode,
        difficulty=difficulty,
        player_x_id=user_id,
        player_o_id=None,
        winner=winner,
        end_reason=EndReason.WIN,
        time_limit_seconds=300,
        started_at=START,
        ended_at=START + timedelta(minutes=5),
        moves=(),
    )


@pytest.mark.asyncio
async def test_stats_need_a_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me/stats")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_new_user_has_empty_stats(client: AsyncClient) -> None:
    token, _ = await register_and_login(client)
    response = await client.get(
        "/api/v1/users/me/stats", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["overall"]["played"] == 0
    assert data["best_streak"] == 0
    assert set(data["by_difficulty"]) == {"easy", "medium", "hard"}


@pytest.mark.asyncio
async def test_stats_count_only_games_against_mochi(
    client: AsyncClient, session_maker: async_sessionmaker[AsyncSession]
) -> None:
    token, user_id = await register_and_login(client)
    async with session_maker() as session:
        repository = SqlMatchRepository(session)
        await repository.add(make_match(user_id, Player.X))
        await repository.add(make_match(user_id, Player.O, difficulty=Difficulty.HARD))
        await repository.add(
            make_match(user_id, Player.X, mode=GameMode.LOCAL, difficulty=None)
        )

    response = await client.get(
        "/api/v1/users/me/stats", headers={"Authorization": f"Bearer {token}"}
    )
    data = response.json()
    assert data["overall"] == {
        "played": 2,
        "wins": 1,
        "losses": 1,
        "draws": 0,
        "win_rate": 0.5,
    }
    assert data["best_streak"] == 1
    assert data["by_difficulty"]["easy"]["wins"] == 1
    assert data["by_difficulty"]["hard"]["losses"] == 1
    assert data["by_difficulty"]["medium"]["played"] == 0
