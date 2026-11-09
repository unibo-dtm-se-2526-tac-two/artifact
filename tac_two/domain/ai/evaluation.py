"""Static evaluation of a Tac2 position, used by the minimax bot.

The score is from the point of view of `player`: positive is good for them,
negative is good for the opponent. It is antisymmetric: evaluating the same
position for the opponent gives the opposite number.
"""

from collections.abc import Sequence

from tac_two.domain.game.common import WIN_LINES, Player
from tac_two.domain.game.game import Game

# How much a small board is worth: the centre and the corners belong to more
# winning lines of the big board, so they matter more.
BOARD_WEIGHT = (3, 2, 3, 2, 4, 2, 3, 2, 3)

BOARD_WON = 30
# Value of a line of the big board that only one player can still complete,
# indexed by how many of its boards that player already owns.
BIG_LINE = (0, 10, 60, 0)
# Same idea inside an open small board.
SMALL_LINE = (0, 1, 5, 0)
# Having the free choice of board is an advantage.
FREE_CHOICE = 8


def _line_value(
    cells: Sequence[Player | None], player: Player, values: tuple[int, ...]
) -> int:
    score = 0
    for a, b, c in WIN_LINES:
        line = (cells[a], cells[b], cells[c])
        mine = sum(1 for owner in line if owner is player)
        theirs = sum(1 for owner in line if owner is player.opponent)
        if theirs == 0:
            score += values[mine]
        elif mine == 0:
            score -= values[theirs]
    return score


def evaluate(game: Game, player: Player) -> int:
    """Score the position of `game` from the point of view of `player`."""
    opponent = player.opponent
    owners = [board.winner for board in game.boards]
    score = _line_value(owners, player, BIG_LINE)

    for index, board in enumerate(game.boards):
        weight = BOARD_WEIGHT[index]
        if board.winner is player:
            score += BOARD_WON * weight
        elif board.winner is opponent:
            score -= BOARD_WON * weight
        elif not board.is_closed:
            score += weight * _line_value(board.cells, player, SMALL_LINE)

    if game.forced_board is None:
        score += FREE_CHOICE if game.current_player is player else -FREE_CHOICE
    return score
