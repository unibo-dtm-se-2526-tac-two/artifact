import pytest

from tac_two.domain.game.clock import DEFAULT_TIME_SECONDS, Clock
from tac_two.domain.game.common import Player

X, O = Player.X, Player.O  # noqa: E741


def test_default_is_five_minutes_each() -> None:
    clock = Clock(now=0)
    assert clock.remaining(X) == 300
    assert clock.remaining(O) == 300
    assert DEFAULT_TIME_SECONDS == 300


def test_only_the_active_player_loses_time() -> None:
    clock = Clock(now=0, initial_seconds=60)
    clock.tick(10)
    assert clock.remaining(X) == 50
    assert clock.remaining(O) == 60


def test_switch_passes_the_turn() -> None:
    clock = Clock(now=0, initial_seconds=60)
    clock.switch(10)
    assert clock.active_player is O
    clock.tick(25)
    assert clock.remaining(X) == 50
    assert clock.remaining(O) == 45


def test_first_player_can_be_o() -> None:
    clock = Clock(now=0, initial_seconds=60, first_player=O)
    clock.tick(5)
    assert clock.remaining(O) == 55
    assert clock.remaining(X) == 60


def test_running_out_of_time_expires_the_player() -> None:
    clock = Clock(now=0, initial_seconds=60)
    assert clock.tick(59.9) is None
    assert clock.tick(61) is X
    assert clock.expired_player is X
    assert clock.remaining(X) == 0


def test_exactly_zero_counts_as_expired() -> None:
    clock = Clock(now=0, initial_seconds=60)
    assert clock.tick(60) is X


def test_switch_does_not_pass_turn_when_mover_timed_out() -> None:
    clock = Clock(now=0, initial_seconds=60)
    assert clock.switch(70) is X
    assert clock.active_player is X


def test_expired_clock_stays_expired_and_stops_counting() -> None:
    clock = Clock(now=0, initial_seconds=60)
    clock.tick(70)
    clock.tick(500)
    assert clock.expired_player is X
    assert clock.remaining(O) == 60


def test_time_cannot_go_backwards() -> None:
    clock = Clock(now=10)
    with pytest.raises(ValueError):
        clock.tick(5)


def test_initial_time_must_be_positive() -> None:
    with pytest.raises(ValueError):
        Clock(now=0, initial_seconds=0)
