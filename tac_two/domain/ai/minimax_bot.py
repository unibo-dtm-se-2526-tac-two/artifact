"""Hard opponent: minimax search with alpha-beta pruning.

The search runs with iterative deepening: it plays a complete search at depth 1,
then 2, then 3 and so on, until it reaches `max_depth` or the time runs out.
When time is up in the middle of a depth, that unfinished depth is thrown away
and the move from the last complete one is used. So the bot always answers, and
never takes (much) longer than `time_limit`.
"""

import random
import time
from collections.abc import Callable

from tac_two.domain.ai.bot import Bot
from tac_two.domain.ai.evaluation import evaluate
from tac_two.domain.ai.greedy_bot import CELL_BONUS, completes_line
from tac_two.domain.game.common import Move, Player
from tac_two.domain.game.game import Game

WIN = 100_000  # bigger than any evaluation
INFINITY = 10**9
CHECK_EVERY = 256  # nodes between two looks at the clock


class _TimeUp(Exception):
    """Raised inside the search when the time limit is reached."""


class MinimaxBot(Bot):
    def __init__(
        self,
        max_depth: int = 6,
        time_limit: float = 1.0,
        rng: random.Random | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_depth < 1:
            raise ValueError("max_depth must be at least 1")
        if time_limit <= 0:
            raise ValueError("time_limit must be positive")
        self._max_depth = max_depth
        self._time_limit = time_limit
        self._rng = rng or random.Random()
        self._clock = clock
        self._deadline: float | None = None
        self._nodes = 0

    def choose_move(self, game: Game) -> Move:
        moves = self._legal_moves(game)
        if len(moves) == 1:
            return moves[0]

        me = game.current_player
        deadline = self._clock() + self._time_limit
        best_moves = moves
        first: Move | None = None
        for depth in range(1, self._max_depth + 1):
            # Depth 1 is cheap and always completes: it guarantees an answer.
            self._deadline = None if depth == 1 else deadline
            self._nodes = 0
            try:
                score, found = self._search_root(game, depth, me, first)
            except _TimeUp:
                break
            best_moves = found
            first = found[0]
            if score >= WIN:  # a forced win: no need to look further
                break
        self._deadline = None
        return self._rng.choice(best_moves)

    def _search_root(
        self, game: Game, depth: int, me: Player, first: Move | None
    ) -> tuple[int, list[Move]]:
        best = -INFINITY
        best_moves: list[Move] = []
        for move in self._ordered(game, first):
            # Searching with the window (best - 1, +inf) gives the exact score
            # of every move that is as good as the best one, so ties are kept.
            alpha = best - 1 if best > -INFINITY else -INFINITY
            game.play(move)
            try:
                score = self._search(game, depth - 1, alpha, INFINITY, me)
            finally:
                game.undo()
            if score > best:
                best, best_moves = score, [move]
            elif score == best:
                best_moves.append(move)
        return best, best_moves

    def _search(self, game: Game, depth: int, alpha: int, beta: int, me: Player) -> int:
        self._nodes += 1
        if (
            self._deadline is not None
            and self._nodes % CHECK_EVERY == 0
            and self._clock() >= self._deadline
        ):
            raise _TimeUp
        if game.is_over:
            if game.winner is None:
                return 0
            # A win found with more depth left is a faster win: prefer it.
            return (WIN + depth) if game.winner is me else -(WIN + depth)
        if depth == 0:
            return evaluate(game, me)

        maximizing = game.current_player is me
        value = -INFINITY if maximizing else INFINITY
        for move in self._ordered(game, None):
            game.play(move)
            try:
                score = self._search(game, depth - 1, alpha, beta, me)
            finally:
                game.undo()
            if maximizing:
                value = max(value, score)
                alpha = max(alpha, value)
            else:
                value = min(value, score)
                beta = min(beta, value)
            if alpha >= beta:
                break
        return value

    @staticmethod
    def _ordered(game: Game, first: Move | None) -> list[Move]:
        """Promising moves first: alpha-beta prunes much more that way."""
        player = game.current_player

        def promise(move: Move) -> int:
            board, cell = move
            cells = game.boards[board].cells
            if move == first:
                return 10_000
            if completes_line(cells, cell, player):
                return 100 + CELL_BONUS[cell]
            if completes_line(cells, cell, player.opponent):
                return 50 + CELL_BONUS[cell]
            return CELL_BONUS[cell]

        return sorted(game.legal_moves(), key=promise, reverse=True)
