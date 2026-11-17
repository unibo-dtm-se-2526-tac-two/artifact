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
from tac_two.api.schemas import UserCreate, UserUpdate

MIN_PASSWORD_LENGTH = 8
# the login token lasts one hour
TOKEN_LIFETIME_SECONDS = 3600


# UserManager is the class FastAPI Users uses to register, update and check users.
# We extend it to add our own rules (password length, unique username).
class UserManager(UUIDIDMixin, BaseUserManager[UserTable, uuid.UUID]):
    def __init__(
        self, user_db: SQLAlchemyUserDatabase[UserTable, uuid.UUID], secret: str
    ) -> None:
        super().__init__(user_db)
        # we keep the database here so we can run our own queries
        self._db = user_db
        self.reset_password_token_secret = secret
        self.verification_token_secret = secret

    async def validate_password(
        self, password: str, user: schemas.UC | models.UP
    ) -> None:
        # the password must have at least 8 characters
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidPasswordException(
                reason=f"Password must have at least {MIN_PASSWORD_LENGTH} characters"
            )

    async def is_username_taken(self, username: str) -> bool:
        # look for a user that already has this username
        query = select(UserTable).where(UserTable.username == username)
        result = await self._db.session.execute(query)
        # if we find someone, the username is already taken
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Request | None = None,
    ) -> UserTable:
        # registration: before creating the user we check the username is free
        # (FastAPI Users only checks the email, not the username)
        if isinstance(user_create, UserCreate):
            taken = await self.is_username_taken(user_create.username)
            if taken:
                raise HTTPException(
                    status_code=400, detail="REGISTER_USERNAME_ALREADY_EXISTS"
                )
        # everything ok: FastAPI Users creates the user
        return await super().create(user_create, safe, request)

    async def update(
        self,
        user_update: schemas.UU,
        user: UserTable,
        safe: bool = False,
        request: Request | None = None,
    ) -> UserTable:
        # profile update: we only check the username if the user sent a new one
        if isinstance(user_update, UserUpdate) and user_update.username is not None:
            new_username = user_update.username
            # saving the profile with the same username as before is fine
            changed = new_username != user.username
            if changed and await self.is_username_taken(new_username):
                raise HTTPException(
                    status_code=400, detail="UPDATE_USER_USERNAME_ALREADY_EXISTS"
                )
        # everything ok: FastAPI Users saves the changes
        return await super().update(user_update, user, safe, request)


# FastAPI calls this function to get a UserManager when a route needs it
async def get_user_manager(
    user_db: Annotated[
        SQLAlchemyUserDatabase[UserTable, uuid.UUID], Depends(get_user_db)
    ],
) -> AsyncIterator[UserManager]:
    yield UserManager(user_db, get_settings().secret_key)


# the frontend sends the token in the header "Authorization: Bearer <token>"
bearer_transport = BearerTransport(tokenUrl="api/v1/auth/login")


# the token is a JWT signed with our secret key
def get_jwt_strategy() -> JWTStrategy[UserTable, uuid.UUID]:
    return JWTStrategy(
        secret=get_settings().secret_key, lifetime_seconds=TOKEN_LIFETIME_SECONDS
    )


# login method: bearer token + JWT
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[UserTable, uuid.UUID](get_user_manager, [auth_backend])

# used in the routes that need a logged-in user (stats, games)
current_active_user = fastapi_users.current_user(active=True)
