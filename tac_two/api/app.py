from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tac_two.api.auth import auth_backend, fastapi_users
from tac_two.api.schemas import UserCreate, UserRead, UserUpdate

FRONTEND_ORIGINS = ["http://localhost:5173"]


def create_app() -> FastAPI:
    app = FastAPI(title="Tac2")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=FRONTEND_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
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
