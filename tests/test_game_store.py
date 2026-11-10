import pytest

from tac_two.adapters.game_store import GameStore
from tac_two.domain.game_session import GameSession
from tac_two.domain.match import GameMode

pytestmark = pytest.mark.asyncio


class FakeTime:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


async def test_a_stored_game_can_be_opened() -> None:
    time = FakeTime()
    store = GameStore(now=time)
    session = GameSession(GameMode.LOCAL, time)
    store.add(session)
    async with store.open(session.id) as found:
        assert found is session


async def test_unknown_game_opens_as_none() -> None:
    store = GameStore(now=FakeTime())
    async with store.open(GameSession(GameMode.LOCAL, FakeTime()).id) as found:
        assert found is None


async def test_games_without_activity_are_forgotten() -> None:
    time = FakeTime()
    store = GameStore(now=time, idle_ttl=100)
    old = GameSession(GameMode.LOCAL, time)
    store.add(old)
    time.now = 50
    kept = GameSession(GameMode.LOCAL, time)
    store.add(kept)
    time.now = 130  # `old` was idle for 130 s, `kept` for 80 s
    store.add(GameSession(GameMode.LOCAL, time))
    async with store.open(old.id) as found:
        assert found is None
    async with store.open(kept.id) as found:
        assert found is kept


async def test_using_a_game_keeps_it_alive() -> None:
    time = FakeTime()
    store = GameStore(now=time, idle_ttl=100)
    session = GameSession(GameMode.LOCAL, time)
    store.add(session)
    time.now = 90
    async with store.open(session.id):
        pass
    time.now = 150  # 60 s since the last use
    store.add(GameSession(GameMode.LOCAL, time))
    async with store.open(session.id) as found:
        assert found is session
