import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tac_two.adapters.database import create_engine
from tac_two.adapters.match_repository import SqlMatchRepository
from tac_two.api.dependencies import get_match_repository


@pytest.mark.asyncio
async def test_match_repository_uses_sql() -> None:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    async with AsyncSession(engine) as session:
        repository = await get_match_repository(session)
        assert isinstance(repository, SqlMatchRepository)
    await engine.dispose()
