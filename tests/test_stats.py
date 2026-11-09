from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from tac_two.domain.ai.factory import Difficulty
from tac_two.domain.game.common import Player
from tac_two.domain.match import EndReason, GameMode, Match
from tac_two.domain.stats import Record, compute_stats

START = datetime(2026, 11, 1, 10, 0, 0, tzinfo=timezone.utc)
SOFIA = uuid4()


def make_match(
    winner: Player | None,
    minutes: int = 5,
    mode: GameMode = GameMode.COMPUTER,
    difficulty: Difficulty | None = Difficulty.EASY,
    player_x_id: UUID | None = SOFIA,
    player_o_id: UUID | None = None,
) -> Match:
    return Match(
        id=uuid4(),
        mode=mode,
        difficulty=difficulty,
        player_x_id=player_x_id,
        player_o_id=player_o_id,
        winner=winner,
        end_reason=EndReason.WIN if winner else EndReason.DRAW,
        time_limit_seconds=300,
        started_at=START,
        ended_at=START + timedelta(minutes=minutes),
        moves=(),
    )


def test_no_matches_gives_empty_stats() -> None:
    stats = compute_stats(SOFIA, [])
    assert stats.overall == Record()
    assert stats.overall.played == 0
    assert stats.overall.win_rate == 0.0
    assert stats.best_streak == 0


def test_wins_losses_and_draws_are_counted() -> None:
    matches = [
        make_match(Player.X),
        make_match(Player.X),
        make_match(Player.O),
        make_match(None),
    ]
    stats = compute_stats(SOFIA, matches)
    assert stats.overall == Record(wins=2, losses=1, draws=1)
    assert stats.overall.played == 4
    assert stats.overall.win_rate == 0.5


def test_win_as_player_o_counts_as_win() -> None:
    match = make_match(Player.O, player_x_id=None, player_o_id=SOFIA)
    assert compute_stats(SOFIA, [match]).overall == Record(wins=1)


def test_stats_are_split_by_difficulty() -> None:
    matches = [
        make_match(Player.X, difficulty=Difficulty.EASY),
        make_match(Player.O, difficulty=Difficulty.HARD),
    ]
    stats = compute_stats(SOFIA, matches)
    assert stats.by_difficulty[Difficulty.EASY] == Record(wins=1)
    assert stats.by_difficulty[Difficulty.MEDIUM] == Record()
    assert stats.by_difficulty[Difficulty.HARD] == Record(losses=1)


def test_local_and_online_matches_are_not_counted() -> None:
    local = make_match(Player.X, mode=GameMode.LOCAL, difficulty=None)
    online = make_match(Player.X, mode=GameMode.ONLINE, difficulty=None)
    stats = compute_stats(SOFIA, [local, online])
    assert stats.overall == Record()
    assert stats.best_streak == 0


def test_best_streak_follows_the_order_of_the_matches() -> None:
    # given newest first, like the repository does
    matches = [
        make_match(Player.X, minutes=60),
        make_match(Player.O, minutes=50),
        make_match(Player.X, minutes=40),
        make_match(Player.X, minutes=30),
        make_match(Player.X, minutes=20),
        make_match(None, minutes=10),
        make_match(Player.X, minutes=5),
    ]
    assert compute_stats(SOFIA, matches).best_streak == 3
