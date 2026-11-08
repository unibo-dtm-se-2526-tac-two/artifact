from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from tac_two.domain.game.common import Move, Player


class GameMode(str, Enum):
    LOCAL = "local"
    COMPUTER = "computer"
    ONLINE = "online"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EndReason(str, Enum):
    NORMAL = "normal"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class Match:
    # A finished match, as it is saved in the match history.

    id: UUID
    mode: GameMode
    difficulty: Difficulty | None
    player_x_id: UUID | None
    player_o_id: UUID | None
    winner: Player | None  # None means the match ended in a draw
    end_reason: EndReason
    time_limit_seconds: int
    started_at: datetime
    ended_at: datetime
    moves: tuple[Move, ...]

    def __post_init__(self) -> None:
        if self.mode == GameMode.COMPUTER and self.difficulty is None:
            raise ValueError("a match against the computer needs a difficulty")
        if self.mode != GameMode.COMPUTER and self.difficulty is not None:
            raise ValueError("only matches against the computer have a difficulty")
        if self.end_reason == EndReason.TIMEOUT and self.winner is None:
            raise ValueError("a match lost on time must have a winner")
        if self.ended_at < self.started_at:
            raise ValueError("a match cannot end before it starts")
