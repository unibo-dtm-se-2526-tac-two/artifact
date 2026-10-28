from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tac_two.adapters.database import create_engine, create_session_maker
from tac_two.adapters.models import Base
from tac_two.api.app import app
from tac_two.api.dependencies import get_session

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/users/me"

NEW_USER = {
    "email": "sofia@example.com",
    "password": "password123",
    "username": "sofia_s",
}


@pytest_asyncio.fixture
async def client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[AsyncClient]:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("SECRET_KEY", "test-secret-with-more-than-thirty-two-characters")

    engine = create_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_maker = create_session_maker(engine)

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    await engine.dispose()


async def login(client: AsyncClient, email: str, password: str) -> str:
    response = await client.post(
        LOGIN_URL, data={"username": email, "password": password}
    )
    assert response.status_code == 200
    return str(response.json()["access_token"])


@pytest.mark.asyncio
async def test_register_creates_a_user(client: AsyncClient) -> None:
    response = await client.post(REGISTER_URL, json=NEW_USER)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == NEW_USER["email"]
    assert body["username"] == NEW_USER["username"]
    assert "password" not in body
    assert "hashed_password" not in body


@pytest.mark.asyncio
async def test_register_rejects_a_used_email(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=NEW_USER)
    other = {**NEW_USER, "username": "other_name"}
    response = await client.post(REGISTER_URL, json=other)
    assert response.status_code == 400
    assert response.json()["detail"] == "REGISTER_USER_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_register_rejects_a_used_username(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=NEW_USER)
    other = {**NEW_USER, "email": "other@example.com"}
    response = await client.post(REGISTER_URL, json=other)
    assert response.status_code == 400
    assert response.json()["detail"] == "REGISTER_USERNAME_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_register_rejects_a_short_password(client: AsyncClient) -> None:
    response = await client.post(REGISTER_URL, json={**NEW_USER, "password": "short"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"


@pytest.mark.asyncio
async def test_register_rejects_a_bad_username(client: AsyncClient) -> None:
    response = await client.post(
        REGISTER_URL, json={**NEW_USER, "username": "sofia scardovi"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_gives_a_token(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=NEW_USER)
    token = await login(client, NEW_USER["email"], NEW_USER["password"])
    assert token != ""


@pytest.mark.asyncio
async def test_login_rejects_a_wrong_password(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=NEW_USER)
    response = await client.post(
        LOGIN_URL, data={"username": NEW_USER["email"], "password": "wrong-password"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


@pytest.mark.asyncio
async def test_me_returns_the_logged_user(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=NEW_USER)
    token = await login(client, NEW_USER["email"], NEW_USER["password"])
    response = await client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == NEW_USER["username"]


@pytest.mark.asyncio
async def test_me_needs_a_token(client: AsyncClient) -> None:
    response = await client.get(ME_URL)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_with_a_token(client: AsyncClient) -> None:
    await client.post(REGISTER_URL, json=NEW_USER)
    token = await login(client, NEW_USER["email"], NEW_USER["password"])
    response = await client.post(
        LOGOUT_URL, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_frontend_origin_is_allowed(client: AsyncClient) -> None:
    response = await client.options(
        REGISTER_URL,
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
