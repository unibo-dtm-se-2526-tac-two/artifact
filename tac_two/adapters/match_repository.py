from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from tac_two.adapters.models import MatchTable
from tac_two.domain.game.common import Move, Player
from tac_two.domain.ai.factory import Difficulty
from tac_two.domain.match import EndReason, GameMode, Match
from tac_two.domain.match_repository import MatchRepository


def as_utc(moment: datetime) -> datetime:
    # SQLite forgets the time zone, PostgreSQL keeps it: always give back UTC
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def to_row(match: Match) -> MatchTable:
    return MatchTable(
        id=match.id,
        mode=match.mode.value,
        difficulty=match.difficulty.value if match.difficulty else None,
        player_x_id=match.player_x_id,
        player_o_id=match.player_o_id,
        winner=match.winner.value if match.winner else None,
        end_reason=match.end_reason.value,
        time_limit_seconds=match.time_limit_seconds,
        started_at=match.started_at,
        ended_at=match.ended_at,
        moves=[list(move) for move in match.moves],
    )


def to_domain(row: MatchTable) -> Match:
    moves: tuple[Move, ...] = tuple((board, cell) for board, cell in row.moves)
    return Match(
        id=row.id,
        mode=GameMode(row.mode),
        difficulty=Difficulty(row.difficulty) if row.difficulty else None,
        player_x_id=row.player_x_id,
        player_o_id=row.player_o_id,
        winner=Player(row.winner) if row.winner else None,
        end_reason=EndReason(row.end_reason),
        time_limit_seconds=row.time_limit_seconds,
        started_at=as_utc(row.started_at),
        ended_at=as_utc(row.ended_at),
        moves=moves,
    )


class SqlMatchRepository(MatchRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, match: Match) -> None:
        self._session.add(to_row(match))
        await self._session.commit()

    async def get_by_id(self, match_id: UUID) -> Match | None:
        row = await self._session.get(MatchTable, match_id)
        return to_domain(row) if row else None

    async def list_by_player(self, user_id: UUID) -> list[Match]:
        query = (
            select(MatchTable)
            .where(
                or_(
                    MatchTable.player_x_id == user_id,
                    MatchTable.player_o_id == user_id,
                )
            )
            .order_by(MatchTable.ended_at.desc())
        )
        rows = (await self._session.execute(query)).scalars().all()
        return [to_domain(row) for row in rows]
