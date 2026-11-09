"""Chess clock: one countdown per player, only the active player's runs.

The clock never reads the system time. Callers pass `now` (in seconds, from any
monotonic source), so tests are instant and an online server can be the one
deciding what time it is.
"""

from tac_two.domain.game.common import Player

DEFAULT_TIME_SECONDS = 300.0  # 5 minutes each


class Clock:
    def __init__(
        self,
        now: float,
        initial_seconds: float = DEFAULT_TIME_SECONDS,
        first_player: Player = Player.X,
    ) -> None:
        """Create the clock and start it: the first player's time runs from `now`."""
        if initial_seconds <= 0:
            raise ValueError("initial_seconds must be positive")
        self._remaining = {Player.X: initial_seconds, Player.O: initial_seconds}
        self._active = first_player
        self._last = now
        self._expired: Player | None = None

    @property
    def active_player(self) -> Player:
        return self._active

    @property
    def expired_player(self) -> Player | None:
        """The player who ran out of time, if any."""
        return self._expired

    def remaining(self, player: Player) -> float:
        return self._remaining[player]

    def tick(self, now: float) -> Player | None:
        """Update the active player's time to `now`.

        Returns the player who ran out of time, or None if everyone has time.
        """
        if now < self._last:
            raise ValueError("time cannot go backwards")
        if self._expired is None:
            self._remaining[self._active] -= now - self._last
            if self._remaining[self._active] <= 0:
                self._remaining[self._active] = 0.0
                self._expired = self._active
        self._last = now
        return self._expired

    def switch(self, now: float) -> Player | None:
        """Account for the time used, then pass the turn to the opponent.

        Call it right after a move. If the mover ran out of time while thinking,
        the turn does not pass and the expired player is returned.
        """
        expired = self.tick(now)
        if expired is None:
            self._active = self._active.opponent
        return expired
