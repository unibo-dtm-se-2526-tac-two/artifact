from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tac_two.adapters.database import create_engine, create_session_maker
from tac_two.adapters.match_repository import SqlMatchRepository
from tac_two.adapters.models import Base, UserTable
from tac_two.domain.game.common import Player
from tac_two.domain.match import Difficulty, EndReason, GameMode, Match

START = datetime(2026, 11, 1, 10, 0, 0, tzinfo=timezone.utc)


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with create_session_maker(engine)() as session:
        yield session
    await engine.dispose()


async def add_user(session: AsyncSession, username: str) -> UUID:
    user = UserTable(
        id=uuid4(),
        email=f"{username}@example.com",
        hashed_password="not-a-real-hash",
        username=username,
    )
    session.add(user)
    await session.commit()
    return user.id


def make_match(
    player_x_id: UUID | None,
    player_o_id: UUID | None = None,
    winner: Player | None = Player.X,
    minutes: int = 5,
) -> Match:
    return Match(
        id=uuid4(),
        mode=GameMode.COMPUTER,
        difficulty=Difficulty.HARD,
        player_x_id=player_x_id,
        player_o_id=player_o_id,
        winner=winner,
        end_reason=EndReason.NORMAL,
        time_limit_seconds=300,
        started_at=START,
        ended_at=START + timedelta(minutes=minutes),
        moves=((4, 4), (4, 0), (0, 8)),
    )


@pytest.mark.asyncio
async def test_saved_match_is_read_back_unchanged(session: AsyncSession) -> None:
    repository = SqlMatchRepository(session)
    match = make_match(await add_user(session, "sofia"))
    await repository.add(match)
    assert await repository.get_by_id(match.id) == match


@pytest.mark.asyncio
async def test_draw_is_saved_without_winner(session: AsyncSession) -> None:
    repository = SqlMatchRepository(session)
    match = make_match(await add_user(session, "sofia"), winner=None)
    await repository.add(match)
    saved = await repository.get_by_id(match.id)
    assert saved is not None
    assert saved.winner is None


@pytest.mark.asyncio
async def test_unknown_match_is_none(session: AsyncSession) -> None:
    repository = SqlMatchRepository(session)
    assert await repository.get_by_id(uuid4()) is None


@pytest.mark.asyncio
async def test_list_by_player_gives_own_matches_newest_first(
    session: AsyncSession,
) -> None:
    repository = SqlMatchRepository(session)
    sofia = await add_user(session, "sofia")
    martina = await add_user(session, "martina")
    older = make_match(sofia, minutes=5)
    newer_as_o = make_match(martina, sofia, minutes=10)
    not_sofia = make_match(martina, minutes=15)
    for match in (older, newer_as_o, not_sofia):
        await repository.add(match)

    assert await repository.list_by_player(sofia) == [newer_as_o, older]
