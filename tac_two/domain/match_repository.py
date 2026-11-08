from abc import ABC, abstractmethod
from uuid import UUID

from tac_two.domain.match import Match


class MatchRepository(ABC):
    @abstractmethod
    async def add(self, match: Match) -> None: ...

    @abstractmethod
    async def get_by_id(self, match_id: UUID) -> Match | None: ...

    @abstractmethod
    async def list_by_player(self, user_id: UUID) -> list[Match]:
        """Return the matches the user played (as X or O), newest first."""
