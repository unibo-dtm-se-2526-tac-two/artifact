import random
import uuid

import pytest

from tac_two.domain.ai.bot import Bot
from tac_two.domain.ai.factory import BotFactory, Difficulty
from tac_two.domain.game.common import GameOverError, IllegalMoveError, Move, Player
from tac_two.domain.game.game import Game
from tac_two.domain.game_session import GameSession
from tac_two.domain.match import EndReason, GameMode

X, O = Player.X, Player.O  # noqa: E741


class FakeTime:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class SlowBot(Bot):
    """Picks the first legal move and 'thinks' for a fixed time."""

    def __init__(self, time: FakeTime, thinking: float) -> None:
        self._time = time
        self._thinking = thinking

    def choose_move(self, game: Game) -> Move:
        self._time.advance(self._thinking)
        return self._legal_moves(game)[0]


def local_session(time: FakeTime, minutes: float | None = 5) -> GameSession:
    return GameSession(GameMode.LOCAL, time, minutes=minutes)


def computer_session(
    time: FakeTime, bot: Bot, minutes: float | None = 5, bot_delay: float = 0.0
) -> GameSession:
    return GameSession(
        GameMode.COMPUTER,
        time,
        minutes=minutes,
        bot=bot,
        difficulty=Difficulty.EASY,
        bot_delay=bot_delay,
    )


def test_computer_mode_needs_a_bot() -> None:
    with pytest.raises(ValueError):
        GameSession(GameMode.COMPUTER, FakeTime())


def test_online_games_are_not_played_with_a_session() -> None:
    with pytest.raises(ValueError):
        GameSession(GameMode.ONLINE, FakeTime())


def test_local_game_alternates_players() -> None:
    session = local_session(FakeTime())
    session.play((4, 2))
    assert session.game.current_player is O
    assert session.game.forced_board == 2
    session.play((2, 0))
    assert session.game.current_player is X
    assert session.moves == [(4, 2), (2, 0)]


def test_clock_runs_for_the_player_to_move() -> None:
    time = FakeTime()
    session = local_session(time)
    time.advance(20)
    session.play((4, 4))  # X used 20 seconds
    time.advance(5)
    session.play((4, 0))  # O used 5 seconds
    assert session.clock is not None
    assert session.clock.remaining(X) == 280
    assert session.clock.remaining(O) == 295


def test_a_game_without_clock_has_no_time_limit() -> None:
    time = FakeTime()
    session = local_session(time, minutes=None)
    assert session.clock is None
    time.advance(10_000)
    session.play((4, 4))
    session.refresh()
    assert not session.game.is_over
    assert local_session(time, minutes=0).clock is None


def test_an_illegal_move_changes_nothing_and_the_clock_keeps_running() -> None:
    time = FakeTime()
    session = local_session(time)
    session.play((4, 2))  # O must play in board 2
    time.advance(10)
    with pytest.raises(IllegalMoveError):
        session.play((5, 5))
    assert session.moves == [(4, 2)]
    assert session.game.current_player is O
    assert session.clock is not None
    assert session.clock.active_player is O
    time.advance(5)
    session.refresh()
    assert session.clock.remaining(O) == 285  # the 15 seconds counted


def test_a_move_after_time_is_up_is_not_played() -> None:
    time = FakeTime()
    session = local_session(time)
    time.advance(301)
    session.play((4, 4))
    assert session.moves == []
    assert session.game.is_over
    assert session.game.winner is O
    assert (
        session.game.end_reason is not None
        and session.game.end_reason.value == "timeout"
    )


def test_refresh_ends_the_game_when_time_runs_out() -> None:
    time = FakeTime()
    session = local_session(time)
    session.play((4, 4))
    time.advance(400)  # O is thinking for too long
    session.refresh()
    assert session.game.winner is X
    assert (
        session.game.end_reason is not None
        and session.game.end_reason.value == "timeout"
    )


def test_playing_after_the_end_is_rejected() -> None:
    time = FakeTime()
    session = local_session(time)
    time.advance(301)
    session.refresh()
    with pytest.raises(GameOverError):
        session.play((4, 4))


def test_bot_answers_right_after_the_move() -> None:
    session = computer_session(
        FakeTime(), BotFactory.create(Difficulty.EASY, random.Random(1))
    )
    session.play((4, 4))
    assert len(session.moves) == 2
    assert session.game.current_player is X
    assert session.moves[1][0] == 4  # the bot had to answer in board 4


def test_bot_thinking_time_counts_on_its_own_clock() -> None:
    time = FakeTime()
    session = computer_session(time, SlowBot(time, thinking=30))
    time.advance(10)
    session.play((4, 4))
    assert session.clock is not None
    assert session.clock.remaining(X) == 290
    assert session.clock.remaining(O) == 270


def test_bot_that_runs_out_of_time_loses() -> None:
    time = FakeTime()
    session = computer_session(time, SlowBot(time, thinking=400))
    session.play((4, 4))
    assert len(session.moves) == 1  # the bot's late move was not played
    assert session.game.winner is X
    assert (
        session.game.end_reason is not None
        and session.game.end_reason.value == "timeout"
    )


def test_the_finished_game_becomes_a_match_to_save() -> None:
    time = FakeTime()
    owner = uuid.uuid4()
    session = GameSession(GameMode.LOCAL, time, minutes=5, owner_id=owner)
    assert session.to_match() is None  # still running
    session.play((4, 4))
    time.advance(500)
    session.refresh()
    match = session.to_match()
    assert match is not None
    assert match.id == session.id
    assert match.mode is GameMode.LOCAL
    assert match.difficulty is None
    assert match.player_x_id == owner
    assert match.player_o_id is None
    assert match.winner is X
    assert match.end_reason is EndReason.TIMEOUT
    assert match.time_limit_seconds == 300
    assert match.moves == ((4, 4),)
    assert match.started_at.tzinfo is not None
    assert match.ended_at >= match.started_at


def test_a_match_against_the_computer_keeps_the_difficulty() -> None:
    time = FakeTime()
    session = computer_session(time, SlowBot(time, thinking=1))
    session.play((4, 4))  # the bot answers
    time.advance(400)  # then X takes too long
    session.refresh()
    match = session.to_match()
    assert match is not None
    assert match.mode is GameMode.COMPUTER
    assert match.difficulty is Difficulty.EASY
    assert match.winner is O  # X took too long


def test_a_game_nobody_played_is_not_saved() -> None:
    time = FakeTime()
    session = GameSession(GameMode.LOCAL, time, minutes=5, owner_id=uuid.uuid4())
    time.advance(400)
    session.refresh()
    assert session.game.is_over  # time ran out...
    assert session.to_match() is None  # ...but there was no match to remember


def test_a_game_without_clock_is_not_saved() -> None:
    time = FakeTime()
    session = GameSession(GameMode.LOCAL, time, minutes=None)
    rng = random.Random(0)
    while not session.game.is_over:
        session.play(rng.choice(session.game.legal_moves()))
    assert session.to_match() is None


def test_a_draw_or_win_is_saved_with_the_right_reason() -> None:
    time = FakeTime()
    rng = random.Random(4)
    session = GameSession(GameMode.LOCAL, time, minutes=5, owner_id=uuid.uuid4())
    while not session.game.is_over:
        session.play(rng.choice(session.game.legal_moves()))
    match = session.to_match()
    assert match is not None
    assert (match.winner is None) == (match.end_reason is EndReason.DRAW)
    assert len(match.moves) == len(session.moves)


def test_full_game_against_each_bot_ends_with_a_result() -> None:
    for difficulty in (Difficulty.EASY, Difficulty.MEDIUM):
        rng = random.Random(3)
        time = FakeTime()
        session = GameSession(
            GameMode.COMPUTER,
            time,
            minutes=None,
            bot=BotFactory.create(difficulty, rng),
            difficulty=difficulty,
        )
        while not session.game.is_over:
            session.play(rng.choice(session.game.legal_moves()))
        assert session.game.is_over


def test_pause_freezes_the_clock() -> None:
    time = FakeTime()
    session = local_session(time)
    time.advance(20)
    session.pause()
    assert session.paused
    time.advance(1000)  # much more than the 300 seconds each player has
    session.refresh()
    assert not session.game.is_over
    assert session.clock is not None
    assert session.clock.remaining(X) == 280
    session.resume()
    assert not session.paused
    time.advance(5)
    session.refresh()
    assert session.clock.remaining(X) == 275


def test_no_move_can_be_played_while_paused() -> None:
    session = local_session(FakeTime())
    session.pause()
    with pytest.raises(IllegalMoveError):
        session.play((4, 4))
    assert session.moves == []
    session.resume()
    session.play((4, 4))
    assert session.moves == [(4, 4)]


def test_pausing_twice_or_resuming_a_running_game_changes_nothing() -> None:
    time = FakeTime()
    session = local_session(time)
    session.resume()  # not paused: nothing to do
    time.advance(10)
    session.pause()
    time.advance(10)
    session.pause()  # it is still paused since the first time
    time.advance(10)
    session.resume()
    assert session.clock is not None
    assert session.clock.remaining(X) == 290


def test_pause_and_resume_are_refused_after_the_end() -> None:
    time = FakeTime()
    session = local_session(time)
    time.advance(301)
    session.refresh()
    with pytest.raises(GameOverError):
        session.pause()
    with pytest.raises(GameOverError):
        session.resume()


def test_pausing_after_time_is_up_ends_the_game_instead() -> None:
    time = FakeTime()
    session = local_session(time)
    time.advance(301)
    session.pause()
    assert session.game.is_over
    assert not session.paused


def test_a_game_without_clock_can_be_paused_too() -> None:
    session = local_session(FakeTime(), minutes=None)
    session.pause()
    with pytest.raises(IllegalMoveError):
        session.play((4, 4))
    session.resume()
    session.play((4, 4))
    assert session.moves == [(4, 4)]


def test_the_bot_delay_cannot_be_negative() -> None:
    bot = BotFactory.create(Difficulty.EASY)
    with pytest.raises(ValueError):
        computer_session(FakeTime(), bot, bot_delay=-1)


def test_a_local_game_has_no_bot_to_wait_for() -> None:
    assert local_session(FakeTime()).bot_move_in is None


def test_the_bot_answers_only_after_its_delay() -> None:
    time = FakeTime()
    session = computer_session(time, SlowBot(time, thinking=0), bot_delay=5)
    session.play((4, 4))
    assert session.moves == [(4, 4)]
    assert session.bot_move_in == 5
    assert session.clock is not None
    assert not session.clock.is_paused  # the bot's clock runs while it waits
    time.advance(4)
    session.refresh()
    assert len(session.moves) == 1
    assert session.bot_move_in == 1
    with pytest.raises(IllegalMoveError):
        session.play((4, 0))  # it is the bot's turn
    time.advance(1)
    session.refresh()
    assert len(session.moves) == 2
    assert session.game.current_player is X
    assert session.bot_move_in is None


def test_the_bots_waiting_time_is_charged_to_the_bot() -> None:
    time = FakeTime()
    session = computer_session(time, SlowBot(time, thinking=0), bot_delay=5)
    session.play((4, 4))
    time.advance(100)  # nobody asks for the state for a long time
    session.refresh()
    assert len(session.moves) == 2  # the bot answered at the right moment
    assert session.clock is not None
    assert session.clock.remaining(O) == 295  # its 5 seconds of waiting
    assert session.clock.remaining(X) == 205  # X's turn began 95 seconds ago


def test_the_bot_loses_if_its_time_runs_out_while_it_waits() -> None:
    time = FakeTime()
    # 0.1 minutes = 6 seconds each, but the bot waits 7.
    session = computer_session(
        time, SlowBot(time, thinking=0), minutes=0.1, bot_delay=7
    )
    session.play((4, 4))
    time.advance(7)
    session.refresh()
    assert session.game.is_over
    assert session.game.winner is X
    assert (
        session.game.end_reason is not None
        and session.game.end_reason.value == "timeout"
    )
    assert len(session.moves) == 1  # the bot never played


def test_pause_freezes_the_bots_wait() -> None:
    time = FakeTime()
    session = computer_session(time, SlowBot(time, thinking=0), bot_delay=5)
    session.play((4, 4))
    time.advance(3)
    session.pause()
    assert session.bot_move_in == 2
    time.advance(1000)
    session.refresh()
    assert len(session.moves) == 1
    session.resume()
    assert session.bot_move_in == 2
    time.advance(1)
    session.refresh()
    assert len(session.moves) == 1
    time.advance(1)
    session.refresh()
    assert len(session.moves) == 2
