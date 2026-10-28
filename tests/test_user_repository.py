from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tac_two.adapters.database import create_engine, create_session_maker
from tac_two.adapters.models import Base, UserTable
from tac_two.adapters.user_repository import SqlUserRepository
from tac_two.domain.user import User


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with create_session_maker(engine)() as db_session:
        db_session.add(
            UserTable(
                id=uuid4(),
                email="sofia@example.com",
                hashed_password="not-a-real-hash",
                username="sofia",
            )
        )
        await db_session.commit()
        yield db_session
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_by_email_returns_a_domain_user(session: AsyncSession) -> None:
    user = await SqlUserRepository(session).get_by_email("sofia@example.com")
    assert isinstance(user, User)
    assert user.username == "sofia"


@pytest.mark.asyncio
async def test_get_by_username_and_by_id_find_the_same_user(
    session: AsyncSession,
) -> None:
    repository = SqlUserRepository(session)
    by_username = await repository.get_by_username("sofia")
    assert by_username is not None
    assert await repository.get_by_id(by_username.id) == by_username


@pytest.mark.asyncio
async def test_unknown_user_returns_none(session: AsyncSession) -> None:
    repository = SqlUserRepository(session)
    assert await repository.get_by_email("nobody@example.com") is None
    assert await repository.get_by_username("nobody") is None
    assert await repository.get_by_id(uuid4()) is None
