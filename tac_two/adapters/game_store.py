"""In-memory storage of the games in progress.

Games live only while the server runs, and are forgotten after a while without
activity. What is worth keeping is saved to the database as a Match.
"""

import asyncio
import time
import uuid
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from tac_two.domain.game_session import GameSession

IDLE_TTL_SECONDS = 3600.0


@dataclass
class _Entry:
    session: GameSession
    last_used: float
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class GameStore:
    def __init__(
        self,
        now: Callable[[], float] = time.monotonic,
        idle_ttl: float = IDLE_TTL_SECONDS,
    ) -> None:
        self.now = now
        self._idle_ttl = idle_ttl
        self._entries: dict[uuid.UUID, _Entry] = {}

    def add(self, session: GameSession) -> None:
        self._purge()
        self._entries[session.id] = _Entry(session, last_used=self.now())

    @asynccontextmanager
    async def open(self, game_id: uuid.UUID) -> AsyncIterator[GameSession | None]:
        """Give exclusive access to a game (None if it does not exist).

        It is an asyncio lock, so a request can wait for the database while
        holding it without blocking the other games.
        """
        entry = self._entries.get(game_id)
        if entry is None:
            yield None
            return
        async with entry.lock:
            entry.last_used = self.now()
            yield entry.session

    def _purge(self) -> None:
        now = self.now()
        idle = [
            game_id
            for game_id, entry in self._entries.items()
            if now - entry.last_used > self._idle_ttl and not entry.lock.locked()
        ]
        for game_id in idle:
            del self._entries[game_id]
