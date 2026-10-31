import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    InvalidPasswordException,
    UUIDIDMixin,
    models,
    schemas,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import select

from tac_two.adapters.models import UserTable
from tac_two.adapters.settings import get_settings
from tac_two.api.dependencies import get_user_db
from tac_two.api.schemas import UserCreate

MIN_PASSWORD_LENGTH = 8
TOKEN_LIFETIME_SECONDS = 3600


class UserManager(UUIDIDMixin, BaseUserManager[UserTable, uuid.UUID]):
    def __init__(
        self, user_db: SQLAlchemyUserDatabase[UserTable, uuid.UUID], secret: str
    ) -> None:
        super().__init__(user_db)
        self._db = user_db
        self.reset_password_token_secret = secret
        self.verification_token_secret = secret

    async def validate_password(
        self, password: str, user: schemas.UC | models.UP
    ) -> None:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidPasswordException(
                reason=f"Password must have at least {MIN_PASSWORD_LENGTH} characters"
            )

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Request | None = None,
    ) -> UserTable:
        if isinstance(user_create, UserCreate):
            query = select(UserTable).where(UserTable.username == user_create.username)
            result = await self._db.session.execute(query)
            if result.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=400, detail="REGISTER_USERNAME_ALREADY_EXISTS"
                )
        return await super().create(user_create, safe, request)


async def get_user_manager(
    user_db: Annotated[
        SQLAlchemyUserDatabase[UserTable, uuid.UUID], Depends(get_user_db)
    ],
) -> AsyncIterator[UserManager]:
    yield UserManager(user_db, get_settings().secret_key)


bearer_transport = BearerTransport(tokenUrl="api/v1/auth/login")


def get_jwt_strategy() -> JWTStrategy[UserTable, uuid.UUID]:
    return JWTStrategy(
        secret=get_settings().secret_key, lifetime_seconds=TOKEN_LIFETIME_SECONDS
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[UserTable, uuid.UUID](get_user_manager, [auth_backend])
