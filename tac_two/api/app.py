from fastapi import FastAPI

from tac_two.api.auth import auth_backend, fastapi_users
from tac_two.api.schemas import UserCreate, UserRead, UserUpdate


def create_app() -> FastAPI:
    app = FastAPI(title="Tac2")
    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/api/v1/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/api/v1/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/api/v1/users",
        tags=["users"],
    )
    return app


app = create_app()
