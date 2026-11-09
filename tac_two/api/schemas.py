import uuid

from fastapi_users import schemas
from pydantic import BaseModel, Field

USERNAME_PATTERN = r"^[A-Za-z0-9_]{3,30}$"


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: str = Field(pattern=USERNAME_PATTERN)


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = Field(default=None, pattern=USERNAME_PATTERN)


class RecordRead(BaseModel):
    played: int
    wins: int
    losses: int
    draws: int
    win_rate: float


class StatsRead(BaseModel):
    overall: RecordRead
    best_streak: int
    by_difficulty: dict[str, RecordRead]
