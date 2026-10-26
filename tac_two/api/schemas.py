import uuid

from fastapi_users import schemas
from pydantic import Field

USERNAME_PATTERN = r"^[A-Za-z0-9_]{3,30}$"


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: str = Field(pattern=USERNAME_PATTERN)


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = Field(default=None, pattern=USERNAME_PATTERN)
