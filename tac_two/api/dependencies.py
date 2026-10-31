import uuid
from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tac_two.adapters.database import create_engine, create_session_maker
from tac_two.adapters.models import UserTable
from tac_two.adapters.settings import get_settings


@lru_cache
def get_session_maker() -> async_sessionmaker[AsyncSession]:
    engine = create_engine(get_settings().database_url)
    return create_session_maker(engine)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_session_maker()() as session:
        yield session


async def get_user_db(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncIterator[SQLAlchemyUserDatabase[UserTable, uuid.UUID]]:
    yield SQLAlchemyUserDatabase(session, UserTable)
