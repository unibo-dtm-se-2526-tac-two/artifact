"""Easy opponent: plays any legal move at random."""

import random

from tac_two.domain.ai.bot import Bot
from tac_two.domain.game.common import Move
from tac_two.domain.game.game import Game


class RandomBot(Bot):
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def choose_move(self, game: Game) -> Move:
        return self._rng.choice(self._legal_moves(game))
