import pytest
from sqlalchemy import text

from tac_two.adapters.database import create_engine


@pytest.mark.asyncio
async def test_engine_can_run_a_query() -> None:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        assert result.scalar() == 1
    await engine.dispose()
