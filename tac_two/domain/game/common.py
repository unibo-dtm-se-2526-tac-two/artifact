"""Building blocks shared by the Tac2 game engine."""

from collections.abc import Sequence
from enum import Enum

# A move is (board, cell): both are indexes 0-8, counted row by row
# (0 = top-left, 2 = top-right, 8 = bottom-right).
Move = tuple[int, int]


class Player(Enum):
    X = "X"
    O = "O"  # noqa: E741

    @property
    def opponent(self) -> "Player":
        return Player.O if self is Player.X else Player.X


WIN_LINES: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def find_winner(cells: Sequence[Player | None]) -> Player | None:
    """Return the player owning a complete line in a 3x3 grid, if any."""
    for a, b, c in WIN_LINES:
        owner = cells[a]
        if owner is not None and owner is cells[b] and owner is cells[c]:
            return owner
    return None


class IllegalMoveError(ValueError):
    """Raised when a move breaks the rules of the game."""


class GameOverError(IllegalMoveError):
    """Raised when a move is attempted after the game has ended."""
