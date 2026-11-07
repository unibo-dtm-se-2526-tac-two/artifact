import random

import pytest

from tac_two.domain.ai.bot import Bot
from tac_two.domain.ai.factory import BotFactory, Difficulty
from tac_two.domain.ai.greedy_bot import GreedyBot, completes_line
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


def play_match(first: Bot, second: Bot, starter: Player) -> Player | None:
    """Play a full game: `first` is X and `second` is O. Returns the winner."""
    game = Game(first_player=starter)
    bots = {X: first, O: second}
    while not game.is_over:
        move = bots[game.current_player].choose_move(game)
        assert move in game.legal_moves()
        game.play(move)
    return game.winner


def test_bot_is_abstract() -> None:
    with pytest.raises(TypeError):
        Bot()  # type: ignore[abstract]


@pytest.mark.parametrize("bot_class", [RandomBot, GreedyBot])
def test_bots_return_a_legal_move_and_leave_the_game_untouched(
    bot_class: type[Bot],
) -> None:
    bot = bot_class(random.Random(1))  # type: ignore[call-arg]
    game = Game()
    game.play((4, 2))
    before = snapshot(game)
    move = bot.choose_move(game)
    assert move in game.legal_moves()
    assert snapshot(game) == before


@pytest.mark.parametrize("bot_class", [RandomBot, GreedyBot])
def test_bots_refuse_to_move_when_the_game_is_over(bot_class: type[Bot]) -> None:
    game = Game()
    game.end_by_timeout(X)
    with pytest.raises(ValueError):
        bot_class().choose_move(game)


def test_random_bot_is_reproducible_with_a_seed() -> None:
    game = Game()
    first = RandomBot(random.Random(7)).choose_move(game)
    second = RandomBot(random.Random(7)).choose_move(game)
    assert first == second


def test_random_bot_respects_the_forced_board() -> None:
    game = Game()
    game.play((4, 6))
    bot = RandomBot(random.Random(3))
    for _ in range(20):
        assert bot.choose_move(game)[0] == 6


def test_completes_line() -> None:
    cells = [X, X, None, None, None, None, None, None, None]
    assert completes_line(cells, 2, X)
    assert not completes_line(cells, 2, O)
    assert not completes_line(cells, 0, X)  # cell already taken


def test_greedy_wins_a_small_board_when_it_can() -> None:
    game = Game()
    mark(game, 4, X, 0, 1)
    assert GreedyBot(random.Random(0)).choose_move(game) == (4, 2)


def test_greedy_blocks_a_small_board_threat() -> None:
    game = Game(first_player=O)
    mark(game, 4, X, 0, 1)
    assert GreedyBot(random.Random(0)).choose_move(game) == (4, 2)


def test_greedy_wins_the_game_when_it_can() -> None:
    game = Game()
    mark(game, 0, X, 0, 1, 2)
    mark(game, 1, X, 0, 1, 2)
    mark(game, 2, X, 0, 1)
    assert GreedyBot(random.Random(0)).choose_move(game) == (2, 2)


@pytest.mark.parametrize("seed", range(10))
def test_greedy_never_hands_the_opponent_an_immediate_win(seed: int) -> None:
    game = Game()
    mark(game, 0, O, 0, 1, 2)
    mark(game, 1, O, 0, 1, 2)
    mark(game, 2, O, 0, 1)  # O threatens to win the game at (2, 2)
    move = GreedyBot(random.Random(seed)).choose_move(game)
    game.play(move)
    for reply in game.legal_moves():
        game.play(reply)
        assert game.winner is not O
        game.undo()


def test_factory_builds_the_right_bot() -> None:
    assert isinstance(BotFactory.create(Difficulty.EASY), RandomBot)
    assert isinstance(BotFactory.create(Difficulty.MEDIUM), GreedyBot)


def test_factory_passes_the_random_generator_to_the_bot() -> None:
    game = Game()
    first = BotFactory.create(Difficulty.EASY, random.Random(5)).choose_move(game)
    second = BotFactory.create(Difficulty.EASY, random.Random(5)).choose_move(game)
    assert first == second


@pytest.mark.parametrize("seed", range(10))
def test_full_games_between_bots_always_finish_with_legal_moves(seed: int) -> None:
    rng = random.Random(seed)
    play_match(GreedyBot(rng), RandomBot(rng), X)
    play_match(RandomBot(rng), GreedyBot(rng), X)


def test_greedy_beats_random_most_of_the_time() -> None:
    wins = 0
    games = 30
    for seed in range(games):
        rng = random.Random(seed)
        greedy_is_x = seed % 2 == 0
        greedy, rand = GreedyBot(rng), RandomBot(rng)
        winner = play_match(
            greedy if greedy_is_x else rand,
            rand if greedy_is_x else greedy,
            X,
        )
        if winner is (X if greedy_is_x else O):
            wins += 1
    assert wins >= 20, f"greedy won only {wins}/{games}"
