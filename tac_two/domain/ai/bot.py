"""Common interface of every computer opponent."""

from abc import ABC, abstractmethod

from tac_two.domain.game.common import Move
from tac_two.domain.game.game import Game


class Bot(ABC):
    """A computer player.

    A bot looks at a game and picks a move. It must leave the game exactly as it
    found it: the caller is the one who plays the chosen move.
    """

    @abstractmethod
    def choose_move(self, game: Game) -> Move:
        """Return a legal move for the current player of `game`."""

    @staticmethod
    def _legal_moves(game: Game) -> list[Move]:
        moves = game.legal_moves()
        if not moves:
            raise ValueError("the game is over: there is no move to choose")
        return moves
