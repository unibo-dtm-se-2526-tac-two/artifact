from typing import Annotated

from fastapi import APIRouter, Depends

from tac_two.adapters.models import UserTable
from tac_two.api.auth import current_active_user
from tac_two.api.dependencies import get_match_repository
from tac_two.api.schemas import RecordRead, StatsRead
from tac_two.domain.match_repository import MatchRepository
from tac_two.domain.stats import Record, compute_stats

router = APIRouter()


def to_record_read(record: Record) -> RecordRead:
    return RecordRead(
        played=record.played,
        wins=record.wins,
        losses=record.losses,
        draws=record.draws,
        win_rate=record.win_rate,
    )


@router.get("/me/stats", response_model=StatsRead)
async def read_my_stats(
    user: Annotated[UserTable, Depends(current_active_user)],
    repository: Annotated[MatchRepository, Depends(get_match_repository)],
) -> StatsRead:
    matches = await repository.list_by_player(user.id)
    stats = compute_stats(user.id, matches)
    return StatsRead(
        overall=to_record_read(stats.overall),
        best_streak=stats.best_streak,
        # the keys are "easy", "medium" and "hard"
        by_difficulty={
            difficulty.value: to_record_read(record)
            for difficulty, record in stats.by_difficulty.items()
        },
    )
