from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from tac_two.domain.ai.factory import Difficulty
from tac_two.domain.game.common import Move, Player


class GameMode(str, Enum):
    LOCAL = "local"
    COMPUTER = "computer"
    ONLINE = "online"


class EndReason(str, Enum):
    WIN = "win"
    DRAW = "draw"
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
        if self.end_reason == EndReason.DRAW and self.winner is not None:
            raise ValueError("a draw cannot have a winner")
        if self.end_reason != EndReason.DRAW and self.winner is None:
            raise ValueError("only a draw can end without a winner")
        if self.ended_at < self.started_at:
            raise ValueError("a match cannot end before it starts")
