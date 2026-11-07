"""Medium opponent: scores every legal move with a simple heuristic.

The heuristic looks only at the move itself and at the opponent's best reply,
it does not search deeper. It takes wins, blocks the opponent's immediate
threats and avoids sending the opponent to a board where they can score.
"""

import random
from collections.abc import Sequence

from tac_two.domain.ai.bot import Bot
from tac_two.domain.game.common import Move, Player, find_winner
from tac_two.domain.game.game import Game

WIN_GAME = 10_000
WIN_SMALL_BOARD = 100
BLOCK_SMALL_BOARD = 60
# Penalties for what the opponent can do right after our move.
OPPONENT_WINS_GAME = 5_000
OPPONENT_WINS_SMALL_BOARD = 70
OPPONENT_FREE_CHOICE = 25
# Small preference for the centre and the corners of a small board.
CELL_BONUS = (2, 0, 2, 0, 3, 0, 2, 0, 2)


def completes_line(cells: Sequence[Player | None], cell: int, player: Player) -> bool:
    """True if `player` placing a mark in `cell` would win this small board."""
    if cells[cell] is not None:
        return False
    trial = list(cells)
    trial[cell] = player
    return find_winner(trial) is player


class GreedyBot(Bot):
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def choose_move(self, game: Game) -> Move:
        moves = self._legal_moves(game)
        scored = [(self._score(game, move), move) for move in moves]
        best = max(score for score, _ in scored)
        return self._rng.choice([move for score, move in scored if score == best])

    def _score(self, game: Game, move: Move) -> int:
        me = game.current_player
        board, cell = move
        cells = game.boards[board].cells

        score = CELL_BONUS[cell]
        if completes_line(cells, cell, me):
            score += WIN_SMALL_BOARD
        elif completes_line(cells, cell, me.opponent):
            score += BLOCK_SMALL_BOARD

        game.play(move)
        try:
            if game.winner is me:
                return WIN_GAME
            if not game.is_over:
                score -= self._opponent_threat(game)
        finally:
            game.undo()
        return score

    @staticmethod
    def _opponent_threat(game: Game) -> int:
        """How much the opponent can gain with their best reply."""
        opponent = game.current_player
        threat = OPPONENT_FREE_CHOICE if game.forced_board is None else 0
        worst = 0
        for board, cell in game.legal_moves():
            if not completes_line(game.boards[board].cells, cell, opponent):
                continue
            worst = max(worst, OPPONENT_WINS_SMALL_BOARD)
            game.play((board, cell))
            try:
                if game.winner is opponent:
                    worst = OPPONENT_WINS_GAME
            finally:
                game.undo()
        return threat + worst
