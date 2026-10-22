import pytest
from sqlalchemy import select

from tac_two.adapters.database import create_engine, create_session_maker
from tac_two.adapters.models import Base, UserTable


@pytest.mark.asyncio
async def test_user_table_saves_a_user() -> None:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_maker = create_session_maker(engine)
    async with session_maker() as session:
        session.add(
            UserTable(
                email="sofia@example.com",
                hashed_password="not-a-real-hash",
                username="sofia",
            )
        )
        await session.commit()

        result = await session.execute(select(UserTable))
        user = result.scalar_one()
        assert user.username == "sofia"
        assert user.email == "sofia@example.com"
        assert user.is_active is True

    await engine.dispose()
