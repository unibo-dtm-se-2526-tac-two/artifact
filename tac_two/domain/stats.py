from dataclasses import dataclass
from uuid import UUID

from tac_two.domain.ai.factory import Difficulty
from tac_two.domain.game.common import Player
from tac_two.domain.match import GameMode, Match


@dataclass(frozen=True)
class Record:
    wins: int = 0
    losses: int = 0
    draws: int = 0

    @property
    def played(self) -> int:
        return self.wins + self.losses + self.draws

    @property
    def win_rate(self) -> float:
        # between 0 and 1, the frontend shows it as a percentage
        if self.played == 0:
            return 0.0
        return self.wins / self.played


@dataclass(frozen=True)
class UserStats:
    overall: Record
    best_streak: int
    by_difficulty: dict[Difficulty, Record]


def side_of(user_id: UUID, match: Match) -> Player:
    return Player.X if match.player_x_id == user_id else Player.O


def has_won(user_id: UUID, match: Match) -> bool:
    return match.winner == side_of(user_id, match)


def make_record(user_id: UUID, matches: list[Match]) -> Record:
    wins = losses = draws = 0
    for match in matches:
        if match.winner is None:
            draws += 1
        elif has_won(user_id, match):
            wins += 1
        else:
            losses += 1
    return Record(wins=wins, losses=losses, draws=draws)


def best_streak(user_id: UUID, matches: list[Match]) -> int:
    # most wins in a row, a draw or a loss starts again from 0
    best = current = 0
    for match in sorted(matches, key=lambda match: match.ended_at):
        if has_won(user_id, match):
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def compute_stats(user_id: UUID, matches: list[Match]) -> UserStats:
    # only games against Mochi count (decided with the group)
    counted = [match for match in matches if match.mode == GameMode.COMPUTER]
    by_difficulty = {
        difficulty: make_record(
            user_id, [match for match in counted if match.difficulty == difficulty]
        )
        for difficulty in Difficulty
    }
    return UserStats(
        overall=make_record(user_id, counted),
        best_streak=best_streak(user_id, counted),
        by_difficulty=by_difficulty,
    )
