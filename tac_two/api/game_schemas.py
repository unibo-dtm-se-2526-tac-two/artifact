import uuid
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Mark = Literal["X", "O"]


class GameCreate(BaseModel):
    mode: Literal["local", "computer"]
    difficulty: Literal["easy", "medium", "hard"] | None = None
    # Minutes for each player. 0 or null means no clock.
    minutes: float | None = Field(default=5, ge=0, le=60)

    @model_validator(mode="after")
    def computer_needs_a_difficulty(self) -> "GameCreate":
        if self.mode == "computer" and self.difficulty is None:
            raise ValueError("difficulty is required in computer mode")
        return self


class MoveIn(BaseModel):
    board: int = Field(ge=0, le=8)
    cell: int = Field(ge=0, le=8)


class MoveOut(BaseModel):
    player: Mark
    board: int
    cell: int


class ClockOut(BaseModel):
    """Seconds left for each player, and whose time is running."""

    x: float
    o: float
    active: Mark | None


class GameState(BaseModel):
    id: uuid.UUID
    mode: Literal["local", "computer"]
    difficulty: Literal["easy", "medium", "hard"] | None
    human_player: Mark | None  # the side played by the person in computer mode
    status: Literal["playing", "finished"]
    current_player: Mark | None  # None once the game is over
    forced_board: int | None  # None: free choice of board
    boards: list[list[Mark | None]]  # 9 boards of 9 cells
    board_winners: list[Literal["X", "O", "draw"] | None]  # one per board
    winner: Mark | None
    end_reason: Literal["win", "draw", "timeout"] | None
    clock: ClockOut | None
    move_count: int
    last_moves: list[MoveOut]  # the last two moves, oldest first
