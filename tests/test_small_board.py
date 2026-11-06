import pytest

from tac_two.domain.game.common import IllegalMoveError, Player
from tac_two.domain.game.small_board import SmallBoard

X, O = Player.X, Player.O # noqa: E741


def fill(board: SmallBoard, moves: dict[int, Player]) -> None:
    for cell, player in moves.items():
        board.place(cell, player)


def test_new_board_is_empty_and_open() -> None:
    board = SmallBoard()
    assert board.winner is None
    assert not board.is_full
    assert not board.is_closed
    assert board.empty_cells() == list(range(9))


@pytest.mark.parametrize(
    "line",
    [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ],
)
def test_every_line_wins(line: tuple[int, int, int]) -> None:
    board = SmallBoard()
    fill(board, {cell: X for cell in line})
    assert board.winner is X
    assert board.is_closed


def test_won_board_is_closed_even_if_not_full() -> None:
    board = SmallBoard()
    fill(board, {0: X, 1: X, 2: X})
    assert not board.is_full
    assert board.is_closed
    assert board.empty_cells() == []
    with pytest.raises(IllegalMoveError):
        board.place(5, O)


def test_full_board_without_line_is_a_draw() -> None:
    board = SmallBoard()
    # X O X / X O O / O X X
    layout = [X, O, X, X, O, O, O, X, X]
    fill(board, dict(enumerate(layout)))
    assert board.is_full
    assert board.is_draw
    assert board.winner is None
    assert board.is_closed


def test_cannot_play_a_taken_cell() -> None:
    board = SmallBoard()
    board.place(4, X)
    with pytest.raises(IllegalMoveError):
        board.place(4, O)


@pytest.mark.parametrize("cell", [-1, 9, 100])
def test_out_of_range_cell_is_rejected(cell: int) -> None:
    with pytest.raises(IllegalMoveError):
        SmallBoard().place(cell, X)


def test_clear_reopens_a_won_board() -> None:
    board = SmallBoard()
    fill(board, {0: X, 1: X, 2: X})
    board.clear(2)
    assert board.winner is None
    assert not board.is_closed
    assert 2 in board.empty_cells()


def test_clear_empty_cell_is_rejected() -> None:
    with pytest.raises(IllegalMoveError):
        SmallBoard().clear(0)