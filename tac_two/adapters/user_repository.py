from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tac_two.adapters.models import UserTable
from tac_two.domain.user import User
from tac_two.domain.user_repository import UserRepository


def to_domain(row: UserTable) -> User:
    return User(id=row.id, email=row.email, username=row.username)


class SqlUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        row = await self._session.get(UserTable, user_id)
        return to_domain(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        query = select(UserTable).filter_by(email=email)
        row = (await self._session.execute(query)).scalar_one_or_none()
        return to_domain(row) if row else None

    async def get_by_username(self, username: str) -> User | None:
        query = select(UserTable).filter_by(username=username)
        row = (await self._session.execute(query)).scalar_one_or_none()
        return to_domain(row) if row else None
