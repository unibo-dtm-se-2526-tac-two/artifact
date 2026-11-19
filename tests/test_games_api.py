import asyncio
import uuid
from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from tac_two.adapters.game_store import GameStore
from tac_two.api.app import app
from tac_two.api.dependencies import get_match_repository
from tac_two.api.games import get_game_store, optional_user
from tac_two.domain.ai.factory import BOT_DELAY_SECONDS, Difficulty
from tac_two.domain.match import EndReason, GameMode, Match
from tac_two.domain.match_repository import MatchRepository

pytestmark = pytest.mark.asyncio

GAMES_URL = "/api/v1/games"


class FakeTime:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class FakeMatchRepository(MatchRepository):
    def __init__(self) -> None:
        self.matches: list[Match] = []
        self.fail_next = False

    async def add(self, match: Match) -> None:
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("database is down")
        self.matches.append(match)

    async def get_by_id(self, match_id: uuid.UUID) -> Match | None:
        return next((m for m in self.matches if m.id == match_id), None)

    async def list_by_player(self, user_id: uuid.UUID) -> list[Match]:
        return [m for m in self.matches if user_id in (m.player_x_id, m.player_o_id)]


class Setup:
    def __init__(self) -> None:
        self.time = FakeTime()
        self.repository = FakeMatchRepository()
        self.user: Any = None  # who is logged in (None: a guest)


@pytest.fixture
def setup() -> Setup:
    state = Setup()
    store = GameStore(now=state.time)
    app.dependency_overrides[get_game_store] = lambda: store
    app.dependency_overrides[get_match_repository] = lambda: state.repository
    app.dependency_overrides[optional_user] = lambda: state.user
    return state


@pytest_asyncio.fixture
async def client(setup: Setup) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()


async def create(client: AsyncClient, **body: Any) -> dict[str, Any]:
    response = await client.post(GAMES_URL, json={"mode": "local", **body})
    assert response.status_code == 201, response.text
    data: dict[str, Any] = response.json()
    return data


async def move(client: AsyncClient, game_id: str, board: int, cell: int) -> Any:
    return await client.post(
        f"{GAMES_URL}/{game_id}/moves", json={"board": board, "cell": cell}
    )


async def read(client: AsyncClient, game_id: str) -> Any:
    return await client.get(f"{GAMES_URL}/{game_id}")


async def test_create_a_local_game(client: AsyncClient) -> None:
    state = await create(client)
    assert state["mode"] == "local"
    assert state["status"] == "playing"
    assert state["current_player"] == "X"
    assert state["forced_board"] is None
    assert state["boards"] == [[None] * 9 for _ in range(9)]
    assert state["board_winners"] == [None] * 9
    assert state["clock"] == {"x": 300, "o": 300, "active": "X", "running": True}
    assert state["paused"] is False
    assert state["bot_move_in"] is None
    assert state["human_player"] is None
    assert state["last_moves"] == []


async def test_a_move_forces_the_next_board(client: AsyncClient) -> None:
    game_id = (await create(client))["id"]
    response = await move(client, game_id, 4, 2)
    assert response.status_code == 200
    state = response.json()
    assert state["boards"][4][2] == "X"
    assert state["current_player"] == "O"
    assert state["forced_board"] == 2
    assert state["last_moves"] == [{"player": "X", "board": 4, "cell": 2}]


async def test_the_game_can_be_read_again(client: AsyncClient) -> None:
    game_id = (await create(client))["id"]
    await move(client, game_id, 4, 2)
    assert (await read(client, game_id)).json()["move_count"] == 1


async def test_an_illegal_move_is_a_conflict_with_a_message(
    client: AsyncClient,
) -> None:
    game_id = (await create(client))["id"]
    await move(client, game_id, 4, 2)
    response = await move(client, game_id, 5, 5)  # O must play in board 2
    assert response.status_code == 409
    assert "board 2" in response.json()["detail"]
    assert (await read(client, game_id)).json()["move_count"] == 1


async def test_unknown_game_is_not_found(client: AsyncClient) -> None:
    assert (await read(client, str(uuid.uuid4()))).status_code == 404
    assert (await move(client, str(uuid.uuid4()), 0, 0)).status_code == 404


@pytest.mark.parametrize(
    "body",
    [
        {"mode": "online"},
        {"mode": "computer"},  # difficulty is required
        {"mode": "computer", "difficulty": "impossible"},
        {"mode": "local", "minutes": -1},
        {"mode": "local", "minutes": 1000},
    ],
)
async def test_invalid_game_requests_are_rejected(
    client: AsyncClient, body: dict[str, Any]
) -> None:
    assert (await client.post(GAMES_URL, json=body)).status_code == 422


@pytest.mark.parametrize("body", [{"board": 9, "cell": 0}, {"board": 0, "cell": -1}])
async def test_moves_out_of_range_are_rejected(
    client: AsyncClient, body: dict[str, int]
) -> None:
    game_id = (await create(client))["id"]
    response = await client.post(f"{GAMES_URL}/{game_id}/moves", json=body)
    assert response.status_code == 422


async def test_computer_answers_after_its_delay(
    client: AsyncClient, setup: Setup
) -> None:
    delay = BOT_DELAY_SECONDS[Difficulty.EASY]
    state = await create(client, mode="computer", difficulty="easy")
    assert state["human_player"] == "X"
    assert state["difficulty"] == "easy"
    first = (await move(client, state["id"], 4, 4)).json()
    assert first["move_count"] == 1
    assert first["current_player"] == "O"
    assert first["bot_move_in"] == delay
    assert first["clock"]["active"] == "O"
    assert first["clock"]["running"] is True  # Mochi's clock runs while it waits
    setup.time.advance(delay)
    after = (await read(client, state["id"])).json()
    assert after["move_count"] == 2
    assert after["current_player"] == "X"
    assert after["bot_move_in"] is None
    assert [m["player"] for m in after["last_moves"]] == ["X", "O"]


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
async def test_every_difficulty_plays(
    client: AsyncClient, setup: Setup, difficulty: str
) -> None:
    state = await create(client, mode="computer", difficulty=difficulty)
    await move(client, state["id"], 4, 4)
    setup.time.advance(BOT_DELAY_SECONDS[Difficulty(difficulty)])
    after = (await read(client, state["id"])).json()
    assert after["move_count"] == 2


async def test_the_clock_decides_the_winner(client: AsyncClient, setup: Setup) -> None:
    game_id = (await create(client))["id"]
    await move(client, game_id, 4, 4)
    setup.time.advance(301)  # O never moves
    state = (await read(client, game_id)).json()
    assert state["status"] == "finished"
    assert state["winner"] == "X"
    assert state["end_reason"] == "timeout"
    assert state["current_player"] is None
    assert state["clock"]["active"] is None


async def test_moves_after_the_end_are_refused(
    client: AsyncClient, setup: Setup
) -> None:
    game_id = (await create(client))["id"]
    setup.time.advance(301)
    await read(client, game_id)
    response = await move(client, game_id, 4, 4)
    assert response.status_code == 409
    assert response.json()["detail"] == "The game is over."


async def test_a_late_move_ends_the_game_instead_of_being_played(
    client: AsyncClient, setup: Setup
) -> None:
    game_id = (await create(client))["id"]
    setup.time.advance(301)
    response = await move(client, game_id, 4, 4)
    assert response.status_code == 200
    state = response.json()
    assert state["move_count"] == 0
    assert state["end_reason"] == "timeout"
    assert state["winner"] == "O"


async def test_zero_minutes_means_no_clock(client: AsyncClient, setup: Setup) -> None:
    state = await create(client, minutes=0)
    assert state["clock"] is None
    setup.time.advance(100_000)
    assert (await read(client, state["id"])).json()["status"] == "playing"


async def test_a_guest_game_is_never_saved(client: AsyncClient, setup: Setup) -> None:
    game_id = (await create(client))["id"]
    setup.time.advance(301)
    await read(client, game_id)
    assert setup.repository.matches == []


async def test_a_logged_in_players_finished_game_is_saved_once(
    client: AsyncClient, setup: Setup
) -> None:
    user_id = uuid.uuid4()
    setup.user = SimpleNamespace(id=user_id)
    game_id = (await create(client, mode="computer", difficulty="medium"))["id"]
    await move(client, game_id, 4, 4)
    setup.time.advance(BOT_DELAY_SECONDS[Difficulty.MEDIUM])
    await read(client, game_id)  # the bot answers
    setup.time.advance(301)  # X never moves again: time out
    await read(client, game_id)
    await read(client, game_id)
    assert len(setup.repository.matches) == 1
    match = setup.repository.matches[0]
    assert match.id == uuid.UUID(game_id)
    assert match.mode is GameMode.COMPUTER
    assert match.difficulty is not None
    assert match.difficulty.value == "medium"
    assert match.player_x_id == user_id
    assert match.player_o_id is None
    assert match.winner is not None
    assert match.winner.value == "O"
    assert match.end_reason is EndReason.TIMEOUT
    assert match.time_limit_seconds == 300
    assert len(match.moves) == 2


async def test_the_match_is_saved_when_the_last_move_ends_the_game(
    client: AsyncClient, setup: Setup
) -> None:
    setup.user = SimpleNamespace(id=uuid.uuid4())
    game_id = (await create(client, mode="computer", difficulty="easy"))["id"]
    await move(client, game_id, 4, 4)
    # The bot answers after its delay, then X runs out of time.
    setup.time.advance(BOT_DELAY_SECONDS[Difficulty.EASY] + 301)
    response = await move(client, game_id, 0, 0)  # too late: the game ends
    assert response.json()["end_reason"] == "timeout"
    assert len(setup.repository.matches) == 1


async def test_a_game_nobody_played_is_not_saved(
    client: AsyncClient, setup: Setup
) -> None:
    setup.user = SimpleNamespace(id=uuid.uuid4())
    game_id = (await create(client))["id"]
    setup.time.advance(301)
    state = (await read(client, game_id)).json()
    assert state["end_reason"] == "timeout"
    assert setup.repository.matches == []


async def test_a_game_without_clock_is_not_saved(
    client: AsyncClient, setup: Setup
) -> None:
    setup.user = SimpleNamespace(id=uuid.uuid4())
    state = await create(client, minutes=0)
    assert state["clock"] is None
    assert setup.repository.matches == []


async def test_a_failed_save_is_retried_by_the_next_request(setup: Setup) -> None:
    setup.user = SimpleNamespace(id=uuid.uuid4())
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        game_id = (await create(client))["id"]
        await move(client, game_id, 4, 4)
        setup.time.advance(301)
        setup.repository.fail_next = True
        assert (await read(client, game_id)).status_code == 500
        assert setup.repository.matches == []
        assert (await read(client, game_id)).status_code == 200
        assert len(setup.repository.matches) == 1
    app.dependency_overrides.clear()


async def test_only_the_owner_can_play_a_logged_in_players_game(
    client: AsyncClient, setup: Setup
) -> None:
    setup.user = SimpleNamespace(id=uuid.uuid4())
    game_id = (await create(client))["id"]
    setup.user = SimpleNamespace(id=uuid.uuid4())  # somebody else
    assert (await read(client, game_id)).status_code == 403
    assert (await move(client, game_id, 4, 4)).status_code == 403
    setup.user = None  # a guest
    assert (await read(client, game_id)).status_code == 403


async def test_two_moves_at_the_same_time_are_played_one_after_the_other(
    client: AsyncClient, setup: Setup
) -> None:
    state = await create(client, mode="computer", difficulty="hard")
    first, second = await asyncio.gather(
        move(client, state["id"], 4, 4), move(client, state["id"], 4, 4)
    )
    assert sorted([first.status_code, second.status_code]) == [200, 409]
    setup.time.advance(BOT_DELAY_SECONDS[Difficulty.HARD])
    assert (await read(client, state["id"])).json()["move_count"] == 2


async def pause(client: AsyncClient, game_id: str) -> Any:
    return await client.post(f"{GAMES_URL}/{game_id}/pause")


async def resume(client: AsyncClient, game_id: str) -> Any:
    return await client.post(f"{GAMES_URL}/{game_id}/resume")


async def test_pause_stops_the_clock(client: AsyncClient, setup: Setup) -> None:
    game_id = (await create(client))["id"]
    await move(client, game_id, 4, 4)
    setup.time.advance(10)
    paused = (await pause(client, game_id)).json()
    assert paused["paused"] is True
    assert paused["clock"]["running"] is False
    assert paused["clock"]["o"] == 290
    setup.time.advance(1000)
    state = (await read(client, game_id)).json()
    assert state["status"] == "playing"
    assert state["clock"]["o"] == 290
    resumed = (await resume(client, game_id)).json()
    assert resumed["paused"] is False
    assert resumed["clock"]["running"] is True
    setup.time.advance(5)
    assert (await read(client, game_id)).json()["clock"]["o"] == 285


async def test_moves_are_refused_while_paused(client: AsyncClient) -> None:
    game_id = (await create(client))["id"]
    await pause(client, game_id)
    response = await move(client, game_id, 4, 4)
    assert response.status_code == 409
    assert response.json()["detail"] == "the game is paused"
    assert (await read(client, game_id)).json()["move_count"] == 0


async def test_pause_and_resume_need_an_existing_game(client: AsyncClient) -> None:
    unknown = str(uuid.uuid4())
    assert (await pause(client, unknown)).status_code == 404
    assert (await resume(client, unknown)).status_code == 404


async def test_only_the_owner_can_pause_a_game(
    client: AsyncClient, setup: Setup
) -> None:
    setup.user = SimpleNamespace(id=uuid.uuid4())
    game_id = (await create(client))["id"]
    setup.user = SimpleNamespace(id=uuid.uuid4())  # somebody else
    assert (await pause(client, game_id)).status_code == 403
    assert (await resume(client, game_id)).status_code == 403


async def test_a_finished_game_cannot_be_paused_or_resumed(
    client: AsyncClient, setup: Setup
) -> None:
    game_id = (await create(client))["id"]
    setup.time.advance(301)
    await read(client, game_id)
    for action in (pause, resume):
        response = await action(client, game_id)
        assert response.status_code == 409
        assert response.json()["detail"] == "The game is over."


async def test_pausing_after_time_is_up_ends_and_saves_the_game(
    client: AsyncClient, setup: Setup
) -> None:
    setup.user = SimpleNamespace(id=uuid.uuid4())
    game_id = (await create(client))["id"]
    await move(client, game_id, 4, 4)
    setup.time.advance(301)
    state = (await pause(client, game_id)).json()
    assert state["end_reason"] == "timeout"
    assert state["paused"] is False
    assert len(setup.repository.matches) == 1


async def test_pause_also_freezes_the_wait_of_the_bot(
    client: AsyncClient, setup: Setup
) -> None:
    delay = BOT_DELAY_SECONDS[Difficulty.EASY]
    game_id = (await create(client, mode="computer", difficulty="easy"))["id"]
    await move(client, game_id, 4, 4)
    setup.time.advance(delay / 2)
    paused = (await pause(client, game_id)).json()
    assert paused["bot_move_in"] == delay / 2
    setup.time.advance(100)
    assert (await read(client, game_id)).json()["move_count"] == 1
    await resume(client, game_id)
    setup.time.advance(delay / 2)
    assert (await read(client, game_id)).json()["move_count"] == 2


async def test_games_against_the_computer_always_have_five_minutes(
    client: AsyncClient,
) -> None:
    for minutes in (0, 1, 60):
        state = await create(
            client, mode="computer", difficulty="easy", minutes=minutes
        )
        assert state["clock"] == {"x": 300, "o": 300, "active": "X", "running": True}


async def test_local_games_keep_the_chosen_time(client: AsyncClient) -> None:
    for minutes in (5, 10, 15):
        state = await create(client, minutes=minutes)
        assert state["clock"]["x"] == minutes * 60
