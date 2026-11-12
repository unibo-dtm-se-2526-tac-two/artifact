import random

import pytest

from tac_two.domain.ai.evaluation import evaluate
from tac_two.domain.ai.factory import BotFactory, Difficulty
from tac_two.domain.ai.greedy_bot import GreedyBot
from tac_two.domain.ai.minimax_bot import CHECK_EVERY, MinimaxBot
from tac_two.domain.ai.random_bot import RandomBot
from tac_two.domain.game.common import Player
from tac_two.domain.game.game import Game

X, O = Player.X, Player.O  # noqa: E741


def snapshot(game: Game) -> tuple[object, ...]:
    return (
        [board.cells for board in game.boards],
        game.current_player,
        game.forced_board,
        game.legal_moves(),
        game.winner,
    )


def mark(game: Game, board: int, player: Player, *cells: int) -> None:
    for cell in cells:
        game._boards[board].place(cell, player)


def random_position(seed: int, plies: int) -> Game:
    rng = random.Random(seed)
    game = Game()
    for _ in range(plies):
        if game.is_over:
            break
        game.play(rng.choice(game.legal_moves()))
    return game


class FakeClock:
    """A clock that advances by one second every time it is read."""

    def __init__(self) -> None:
        self.now = 0.0
        self.reads = 0

    def __call__(self) -> float:
        self.reads += 1
        self.now += 1.0
        return self.now


def test_invalid_settings_are_rejected() -> None:
    with pytest.raises(ValueError):
        MinimaxBot(max_depth=0)
    with pytest.raises(ValueError):
        MinimaxBot(time_limit=0)


def test_refuses_to_move_when_the_game_is_over() -> None:
    game = Game()
    game.end_by_timeout(X)
    with pytest.raises(ValueError):
        MinimaxBot().choose_move(game)


def test_returns_the_only_legal_move_without_searching() -> None:
    game = Game()
    # Board 0: eight cells played without a line, only cell 8 is free.
    layout = {0: X, 1: O, 2: X, 3: X, 4: O, 5: O, 6: O, 7: X}
    for cell, player in layout.items():
        mark(game, 0, player, cell)
    game.play((4, 0))  # sends the opponent to board 0
    assert game.legal_moves() == [(0, 8)]
    assert MinimaxBot().choose_move(game) == (0, 8)


def test_wins_the_game_when_it_can() -> None:
    game = Game()
    mark(game, 0, X, 0, 1, 2)
    mark(game, 1, X, 0, 1, 2)
    mark(game, 2, X, 0, 1)
    bot = MinimaxBot(max_depth=1, time_limit=10, rng=random.Random(0))
    assert bot.choose_move(game) == (2, 2)


@pytest.mark.parametrize("seed", range(10))
def test_never_hands_the_opponent_an_immediate_win(seed: int) -> None:
    game = Game()
    mark(game, 0, O, 0, 1, 2)
    mark(game, 1, O, 0, 1, 2)
    mark(game, 2, O, 0, 1)  # O wins the game by reaching (2, 2)
    bot = MinimaxBot(max_depth=2, time_limit=10, rng=random.Random(seed))
    game.play(bot.choose_move(game))
    for reply in game.legal_moves():
        game.play(reply)
        assert game.winner is not O
        game.undo()


def test_prefers_a_faster_win() -> None:
    game = Game()
    mark(game, 0, X, 0, 1, 2)
    mark(game, 1, X, 0, 1, 2)
    mark(game, 2, X, 0, 1)
    mark(game, 3, X, 0, 1, 2)  # also a won board, so X has many ways to win
    bot = MinimaxBot(max_depth=4, time_limit=10, rng=random.Random(1))
    move = bot.choose_move(game)
    game.play(move)
    assert game.winner is X  # it wins at once instead of delaying


def test_leaves_the_game_untouched() -> None:
    game = random_position(seed=5, plies=12)
    before = snapshot(game)
    move = MinimaxBot(max_depth=3, time_limit=10, rng=random.Random(0)).choose_move(
        game
    )
    assert move in game.legal_moves()
    assert snapshot(game) == before


def test_stops_when_time_is_up_and_leaves_the_game_untouched() -> None:
    game = random_position(seed=2, plies=6)
    before = snapshot(game)
    clock = FakeClock()
    bot = MinimaxBot(max_depth=30, time_limit=3, clock=clock)
    move = bot.choose_move(game)
    assert move in game.legal_moves()
    assert snapshot(game) == before
    # The deadline is 3 fake seconds away: the search must stop after a few
    # reads of the clock, not run to depth 30.
    assert clock.reads <= 6
    assert CHECK_EVERY > 1


def test_gives_a_legal_move_even_with_no_time_at_all() -> None:
    game = Game()
    clock = FakeClock()
    bot = MinimaxBot(max_depth=5, time_limit=0.5, clock=clock)
    assert bot.choose_move(game) in game.legal_moves()


def test_same_seed_gives_the_same_move() -> None:
    game = random_position(seed=8, plies=10)
    first = MinimaxBot(max_depth=3, time_limit=10, rng=random.Random(4)).choose_move(
        game
    )
    second = MinimaxBot(max_depth=3, time_limit=10, rng=random.Random(4)).choose_move(
        game
    )
    assert first == second


@pytest.mark.parametrize("seed", range(15))
def test_evaluation_is_opposite_for_the_two_players(seed: int) -> None:
    game = random_position(seed, plies=seed * 3)
    if game.is_over:
        return
    assert evaluate(game, X) == -evaluate(game, O)


def test_evaluation_prefers_the_player_with_more_boards() -> None:
    game = Game()
    mark(game, 4, X, 0, 1, 2)  # X owns the centre board
    game.play((0, 0))
    assert evaluate(game, X) > 0
    assert evaluate(game, O) < 0


def test_move_ordering_puts_winning_moves_first() -> None:
    game = Game()
    mark(game, 4, X, 0, 1)
    ordered = MinimaxBot._ordered(game, None)
    assert ordered[0] == (4, 2)
    assert sorted(ordered) == sorted(game.legal_moves())


@pytest.mark.parametrize("seed", range(3))
def test_full_game_against_random_is_legal_and_won(seed: int) -> None:
    rng = random.Random(seed)
    bots = {
        X: MinimaxBot(max_depth=2, time_limit=10, rng=rng),
        O: RandomBot(rng),
    }
    game = Game()
    while not game.is_over:
        move = bots[game.current_player].choose_move(game)
        assert move in game.legal_moves()
        game.play(move)
    assert game.winner is X


def test_beats_the_greedy_bot_most_of_the_time() -> None:
    wins = 0
    games = 10
    for seed in range(games):
        rng = random.Random(seed)
        minimax_is_x = seed % 2 == 0
        minimax = MinimaxBot(max_depth=3, time_limit=30, rng=rng)
        bots = {
            X: minimax if minimax_is_x else GreedyBot(rng),
            O: GreedyBot(rng) if minimax_is_x else minimax,
        }
        game = Game()
        while not game.is_over:
            game.play(bots[game.current_player].choose_move(game))
        if game.winner is (X if minimax_is_x else O):
            wins += 1
    assert wins >= 7, f"minimax won only {wins}/{games}"


def test_factory_builds_the_hard_bot() -> None:
    assert isinstance(BotFactory.create(Difficulty.HARD), MinimaxBot)


def test_a_real_time_limit_is_respected() -> None:
    import time

    game = random_position(seed=3, plies=8)
    bot = MinimaxBot(max_depth=30, time_limit=0.2, rng=random.Random(0))
    start = time.monotonic()
    move = bot.choose_move(game)
    elapsed = time.monotonic() - start
    assert move in game.legal_moves()
    assert elapsed < 2.0, f"took {elapsed:.2f}s with a 0.2s limit"
