from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from tac_two.domain.game.common import Player
from tac_two.domain.ai.factory import Difficulty
from tac_two.domain.match import EndReason, GameMode, Match

START = datetime(2026, 11, 1, 10, 0, 0)


def make_match(
    mode: GameMode = GameMode.COMPUTER,
    difficulty: Difficulty | None = Difficulty.EASY,
    winner: Player | None = Player.X,
    end_reason: EndReason = EndReason.WIN,
    ended_at: datetime = START + timedelta(minutes=5),
) -> Match:
    return Match(
        id=uuid4(),
        mode=mode,
        difficulty=difficulty,
        player_x_id=uuid4(),
        player_o_id=None,
        winner=winner,
        end_reason=end_reason,
        time_limit_seconds=300,
        started_at=START,
        ended_at=ended_at,
        moves=((4, 4), (4, 0)),
    )


def test_computer_match_keeps_its_data() -> None:
    match = make_match()
    assert match.mode == GameMode.COMPUTER
    assert match.difficulty == Difficulty.EASY
    assert match.winner == Player.X
    assert match.moves == ((4, 4), (4, 0))


def test_computer_match_needs_a_difficulty() -> None:
    with pytest.raises(ValueError):
        make_match(difficulty=None)


@pytest.mark.parametrize("mode", [GameMode.LOCAL, GameMode.ONLINE])
def test_other_modes_have_no_difficulty(mode: GameMode) -> None:
    with pytest.raises(ValueError):
        make_match(mode=mode, difficulty=Difficulty.EASY)
    assert make_match(mode=mode, difficulty=None).difficulty is None


def test_draw_has_no_winner() -> None:
    assert make_match(winner=None, end_reason=EndReason.DRAW).winner is None


def test_draw_cannot_have_a_winner() -> None:
    with pytest.raises(ValueError):
        make_match(winner=Player.X, end_reason=EndReason.DRAW)


def test_win_needs_a_winner() -> None:
    with pytest.raises(ValueError):
        make_match(winner=None, end_reason=EndReason.WIN)


def test_timeout_needs_a_winner() -> None:
    with pytest.raises(ValueError):
        make_match(winner=None, end_reason=EndReason.TIMEOUT)


def test_match_cannot_end_before_it_starts() -> None:
    with pytest.raises(ValueError):
        make_match(ended_at=START - timedelta(minutes=1))
