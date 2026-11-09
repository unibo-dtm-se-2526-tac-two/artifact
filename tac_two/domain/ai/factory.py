"""Creates the right bot for a difficulty level."""

import random
from enum import Enum

from tac_two.domain.ai.bot import Bot
from tac_two.domain.ai.greedy_bot import GreedyBot
from tac_two.domain.ai.minimax_bot import MinimaxBot
from tac_two.domain.ai.random_bot import RandomBot


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class BotFactory:
    @staticmethod
    def create(difficulty: Difficulty, rng: random.Random | None = None) -> Bot:
        if difficulty is Difficulty.EASY:
            return RandomBot(rng)
        if difficulty is Difficulty.MEDIUM:
            return GreedyBot(rng)
        if difficulty is Difficulty.HARD:
            return MinimaxBot(rng=rng)
        raise ValueError(f"unknown difficulty: {difficulty}")
