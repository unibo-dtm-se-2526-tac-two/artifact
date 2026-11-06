"""A single 3x3 tic-tac-toe board, one of the nine that make up a Tac2 game."""

from tac_two.domain.game.common import IllegalMoveError, Player, find_winner

CELLS = 9


class SmallBoard:
    def __init__(self) -> None:
        self._cells: list[Player | None] = [None] * CELLS
        self._winner: Player | None = None

    @property
    def cells(self) -> tuple[Player | None, ...]:
        return tuple(self._cells)

    @property
    def winner(self) -> Player | None:
        return self._winner

    @property
    def is_full(self) -> bool:
        return all(cell is not None for cell in self._cells)

    @property
    def is_draw(self) -> bool:
        return self.is_full and self._winner is None

    @property
    def is_closed(self) -> bool:
        """A board is closed once it is won or full: nobody can play in it."""
        return self._winner is not None or self.is_full

    def empty_cells(self) -> list[int]:
        """Cells that can be played. Empty if the board is closed."""
        if self.is_closed:
            return []
        return [i for i, cell in enumerate(self._cells) if cell is None]

    def place(self, cell: int, player: Player) -> None:
        if not 0 <= cell < CELLS:
            raise IllegalMoveError(f"cell {cell} is out of range")
        if self.is_closed:
            raise IllegalMoveError("this board is already won or full")
        if self._cells[cell] is not None:
            raise IllegalMoveError(f"cell {cell} is already taken")
        self._cells[cell] = player
        self._winner = find_winner(self._cells)

    def clear(self, cell: int) -> None:
        """Undo a placement. Used by the AI to try moves and take them back."""
        if not 0 <= cell < CELLS:
            raise IllegalMoveError(f"cell {cell} is out of range")
        if self._cells[cell] is None:
            raise IllegalMoveError(f"cell {cell} is already empty")
        self._cells[cell] = None
        self._winner = find_winner(self._cells)
