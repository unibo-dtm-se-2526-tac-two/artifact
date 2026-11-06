"""The full Tac2 game: nine small boards and the forced-board rule."""

from dataclasses import dataclass
from enum import Enum

from tac_two.domain.game.common import (
    GameOverError,
    IllegalMoveError,
    Move,
    Player,
    find_winner,
)
from tac_two.domain.game.small_board import CELLS, SmallBoard


class EndReason(Enum):
    WIN = "win"  # three small boards in a row
    DRAW = "draw"  # every small board closed, nobody has a line
    TIMEOUT = "timeout"  # a player ran out of time


@dataclass(frozen=True)
class _Snapshot:
    """What `undo` needs to restore after a move."""

    move: Move
    player: Player
    forced_board: int | None
    winner: Player | None
    end_reason: EndReason | None


class Game:
    def __init__(self, first_player: Player = Player.X) -> None:
        self._boards = [SmallBoard() for _ in range(CELLS)]
        self._current = first_player
        self._forced_board: int | None = None  # first move is free
        self._winner: Player | None = None
        self._end_reason: EndReason | None = None
        self._history: list[_Snapshot] = []

    @property
    def boards(self) -> tuple[SmallBoard, ...]:
        return tuple(self._boards)

    @property
    def current_player(self) -> Player:
        return self._current

    @property
    def forced_board(self) -> int | None:
        """Board the current player must play in, or None if free choice."""
        return self._forced_board

    @property
    def winner(self) -> Player | None:
        return self._winner

    @property
    def end_reason(self) -> EndReason | None:
        return self._end_reason

    @property
    def is_over(self) -> bool:
        return self._end_reason is not None

    def legal_moves(self) -> list[Move]:
        if self.is_over:
            return []
        if self._forced_board is not None:
            targets = [self._forced_board]
        else:
            targets = list(range(CELLS))
        return [
            (board, cell)
            for board in targets
            for cell in self._boards[board].empty_cells()
        ]

    def play(self, move: Move) -> None:
        if self.is_over:
            raise GameOverError("the game is already over")
        board, cell = move
        if not 0 <= board < CELLS:
            raise IllegalMoveError(f"board {board} is out of range")
        if self._forced_board is not None and board != self._forced_board:
            raise IllegalMoveError(f"you must play in board {self._forced_board}")

        player = self._current
        snapshot = _Snapshot(
            move, player, self._forced_board, self._winner, self._end_reason
        )
        self._boards[board].place(cell, player)  # raises if illegal
        self._history.append(snapshot)

        big_winner = find_winner([b.winner for b in self._boards])
        if big_winner is not None:
            self._winner = big_winner
            self._end_reason = EndReason.WIN
            self._forced_board = None
        elif all(b.is_closed for b in self._boards):
            self._end_reason = EndReason.DRAW
            self._forced_board = None
        else:
            # The cell played sends the opponent to the board in that position,
            # unless that board is closed: then the opponent chooses freely.
            self._forced_board = None if self._boards[cell].is_closed else cell
            self._current = player.opponent

    def undo(self) -> None:
        if not self._history:
            raise IllegalMoveError("no move to undo")
        if self._end_reason is EndReason.TIMEOUT:
            raise IllegalMoveError("cannot undo after a timeout")
        snapshot = self._history.pop()
        board, cell = snapshot.move
        self._boards[board].clear(cell)
        self._current = snapshot.player
        self._forced_board = snapshot.forced_board
        self._winner = snapshot.winner
        self._end_reason = snapshot.end_reason

    def end_by_timeout(self, loser: Player) -> None:
        """Finish the game because `loser` ran out of time. The opponent wins."""
        if self.is_over:
            raise GameOverError("the game is already over")
        self._winner = loser.opponent
        self._end_reason = EndReason.TIMEOUT
