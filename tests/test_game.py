import random

import pytest

from tac_two.domain.game.clock import Clock
from tac_two.domain.game.common import GameOverError, IllegalMoveError, Player
from tac_two.domain.game.game import EndReason, Game

X, O = Player.X, Player.O  # noqa: E741


def play_all(game: Game, moves: list[tuple[int, int]]) -> None:
    for move in moves:
        game.play(move)


def test_new_game_first_move_is_free() -> None:
    game = Game()
    assert game.current_player is X
    assert game.forced_board is None
    assert len(game.legal_moves()) == 81


def test_first_player_can_be_chosen() -> None:
    assert Game(first_player=O).current_player is O


def test_cell_played_forces_the_opponent_board() -> None:
    game = Game()
    game.play((4, 2))  # cell 2 = top-right
    assert game.current_player is O
    assert game.forced_board == 2
    assert {board for board, _ in game.legal_moves()} == {2}


def test_playing_outside_the_forced_board_is_rejected() -> None:
    game = Game()
    game.play((4, 2))
    with pytest.raises(IllegalMoveError):
        game.play((5, 0))
    assert game.current_player is O  # state untouched


def test_taken_cell_is_rejected_and_state_untouched() -> None:
    game = Game()
    game.play((2, 2))  # sends O to board 2
    with pytest.raises(IllegalMoveError):
        game.play((2, 2))
    assert game.current_player is O
    assert game.forced_board == 2


@pytest.mark.parametrize("move", [(-1, 0), (9, 0), (0, -1), (0, 9)])
def test_out_of_range_moves_are_rejected(move: tuple[int, int]) -> None:
    with pytest.raises(IllegalMoveError):
        Game().play(move)


def test_sent_to_a_won_board_means_free_choice() -> None:
    game = Game()
    for cell in (0, 1, 2):
        game._boards[0].place(cell, O)  # board 0 already won by O
    assert game.boards[0].winner is O
    game.play((4, 0))  # cell 0 would send the opponent to board 0, which is closed
    assert game.forced_board is None
    assert game.current_player is O
    legal_boards = {board for board, _ in game.legal_moves()}
    assert 0 not in legal_boards
    assert len(legal_boards) > 1


def test_sent_to_an_open_board_that_is_partly_played_still_forces_it() -> None:
    game = Game()
    game._boards[0].place(0, O)
    game.play((4, 0))
    assert game.forced_board == 0


def test_sent_to_a_full_board_means_free_choice() -> None:
    game = Game()
    # Fill board 8 completely without a line: X O X / X O O / O X X
    layout = [X, O, X, X, O, O, O, X, X]
    for cell, player in enumerate(layout):
        game._boards[8].place(cell, player)  # arrange position directly
    assert game.boards[8].is_draw
    game.play((4, 8))  # sends O to board 8, which is closed
    assert game.forced_board is None
    assert all(board != 8 for board, _ in game.legal_moves())


def arrange_win(game: Game, owner: Player, boards: tuple[int, ...]) -> None:
    for index in boards:
        for cell in (0, 1, 2):
            game._boards[index].place(cell, owner)


def test_three_small_boards_in_a_line_win_the_game() -> None:
    game = Game()
    arrange_win(game, X, (0, 1))
    for cell in (0, 1):
        game._boards[2].place(cell, X)
    game.play((2, 2))  # X completes board 2 -> boards 0,1,2 are X
    assert game.is_over
    assert game.winner is X
    assert game.end_reason is EndReason.WIN


def test_small_draws_do_not_count_for_either_player() -> None:
    game = Game()
    layout = [X, O, X, X, O, O, O, X, X]
    for index in (0, 1, 2):
        for cell, player in enumerate(layout):
            game._boards[index].place(cell, player)
    assert game.boards[0].is_draw
    game.play((3, 0))
    assert game.winner is None
    assert not game.is_over


def test_global_draw_when_every_board_closes_without_a_line() -> None:
    game = Game()
    layout = [X, O, X, X, O, O, O, X, X]
    # Boards won alternately so that no line of three boards forms.
    owners = [X, O, X, O, X, O, O, X, O]
    # 0 X,1 O,2 X / 3 O,4 X,5 O / 6 O,7 X,8 O -> no line
    for index, owner in enumerate(owners):
        board = game._boards[index]
        if index == 8:
            continue
        for cell in (0, 1, 2):
            board.place(cell, owner)
    last = game._boards[8]
    for cell, player in enumerate(layout[:8]):
        last.place(cell, player)  # board 8 left with one empty cell (8), no line
    assert not last.is_closed
    game.play((8, 8))
    assert game.is_over
    assert game.winner is None
    assert game.end_reason is EndReason.DRAW


def test_no_moves_after_the_game_is_over() -> None:
    game = Game()
    arrange_win(game, X, (0, 1))
    for cell in (0, 1):
        game._boards[2].place(cell, X)
    game.play((2, 2))
    assert game.legal_moves() == []
    with pytest.raises(GameOverError):
        game.play((3, 0))


def test_timeout_makes_the_opponent_win_even_when_behind() -> None:
    game = Game()
    arrange_win(game, O, (0, 1))  # O is far ahead
    game.end_by_timeout(O)
    assert game.winner is X
    assert game.end_reason is EndReason.TIMEOUT
    with pytest.raises(GameOverError):
        game.play((4, 4))


def test_timeout_cannot_be_applied_twice() -> None:
    game = Game()
    game.end_by_timeout(X)
    with pytest.raises(GameOverError):
        game.end_by_timeout(O)


def test_undo_restores_everything() -> None:
    game = Game()
    game.play((4, 2))
    game.play((2, 7))
    game.undo()
    assert game.current_player is O
    assert game.forced_board == 2
    assert game.boards[2].cells[7] is None
    game.undo()
    assert game.current_player is X
    assert game.forced_board is None
    assert len(game.legal_moves()) == 81


def test_undo_reopens_a_finished_game() -> None:
    game = Game()
    arrange_win(game, X, (0, 1))
    for cell in (0, 1):
        game._boards[2].place(cell, X)
    game.play((2, 2))
    game.undo()
    assert not game.is_over
    assert game.winner is None
    assert game.current_player is X


def test_undo_with_no_history_or_after_timeout_is_rejected() -> None:
    game = Game()
    with pytest.raises(IllegalMoveError):
        game.undo()
    game.play((0, 0))
    game.end_by_timeout(O)
    with pytest.raises(IllegalMoveError):
        game.undo()


def test_clock_and_game_together_timeout_flow() -> None:
    game = Game()
    clock = Clock(now=0, initial_seconds=60)
    game.play((4, 4))
    assert clock.switch(10) is None
    # O thinks too long
    expired = clock.switch(100)
    assert expired is O
    game.end_by_timeout(expired)
    assert game.winner is X
    assert game.legal_moves() == []


@pytest.mark.parametrize("seed", range(30))
def test_random_games_respect_the_rules_and_undo_back_to_start(seed: int) -> None:
    rng = random.Random(seed)
    game = Game()
    played = 0
    while not game.is_over:
        moves = game.legal_moves()
        assert moves, "a running game always has a legal move"
        forced = game.forced_board
        if forced is not None:
            assert {b for b, _ in moves} == {forced}
        move = rng.choice(moves)
        mover = game.current_player
        game.play(move)
        played += 1
        if not game.is_over:
            assert game.current_player is mover.opponent
            expected = None if game.boards[move[1]].is_closed else move[1]
            assert game.forced_board == expected
    assert game.end_reason in (EndReason.WIN, EndReason.DRAW)
    assert (game.winner is None) == (game.end_reason is EndReason.DRAW)
    for _ in range(played):
        game.undo()
    assert not game.is_over
    assert len(game.legal_moves()) == 81
    assert all(not b.is_closed and b.cells == (None,) * 9 for b in game.boards)
