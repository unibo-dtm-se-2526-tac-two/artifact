"""A game being played: the rules, the chess clock and, optionally, a bot.

This is where the pieces of the engine meet. It stays pure Python (no FastAPI,
no database) and never reads the system time by itself: the caller gives it a
time source, so tests are instant and the server is the only one deciding what
time it is.
"""

import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from tac_two.domain.ai.bot import Bot
from tac_two.domain.ai.factory import Difficulty
from tac_two.domain.game.clock import Clock
from tac_two.domain.game.common import GameOverError, IllegalMoveError, Move, Player
from tac_two.domain.game.game import Game
from tac_two.domain.match import EndReason, GameMode, Match

HUMAN = Player.X  # against the computer the person always plays X


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class GameSession:
    def __init__(
        self,
        mode: GameMode,
        now: Callable[[], float],
        minutes: float | None = 5.0,
        bot: Bot | None = None,
        difficulty: Difficulty | None = None,
        owner_id: uuid.UUID | None = None,
        wall_clock: Callable[[], datetime] = utc_now,
    ) -> None:
        """`minutes` is the time of each player; None or 0 means no clock.

        `now` measures durations (seconds, any monotonic source); `wall_clock`
        gives the real date and time, only used to date the saved match.
        """
        if mode is GameMode.ONLINE:
            raise ValueError("online games are not played with a GameSession")
        if mode is GameMode.COMPUTER and (bot is None or difficulty is None):
            raise ValueError("computer mode needs a bot and a difficulty")
        self.id = uuid.uuid4()
        self.mode = mode
        self.difficulty = difficulty
        self.owner_id = owner_id
        self.minutes = minutes or None
        self.recorded = False  # set once the match has been saved
        self._now = now
        self._wall_clock = wall_clock
        self._bot = bot
        self._game = Game()
        self._moves: list[Move] = []
        self._started_at = now()
        self._started_utc = wall_clock()
        self._finished_at: float | None = None
        self._ended_utc: datetime | None = None
        self._clock = (
            Clock(self._started_at, self.minutes * 60) if self.minutes else None
        )

    @property
    def game(self) -> Game:
        return self._game

    @property
    def clock(self) -> Clock | None:
        return self._clock

    @property
    def moves(self) -> list[Move]:
        return list(self._moves)

    def refresh(self) -> None:
        """Bring the clock up to date: ends the game if someone ran out of time."""
        self._timed_out(self._now())

    def play(self, move: Move) -> None:
        """Play a move for the current player. In computer mode the bot answers.

        If the player's time is already up, the move is not played and the game
        ends with a timeout instead.
        """
        now = self._now()
        if self._game.is_over:
            raise GameOverError("the game is already over")
        if self._timed_out(now):
            return
        if self.mode is GameMode.COMPUTER and self._game.current_player is not HUMAN:
            raise IllegalMoveError("it is not your turn")
        self._play_and_pass_turn(move, now)
        if self.mode is GameMode.COMPUTER and not self._game.is_over:
            self._bot_turn()

    def to_match(self) -> Match | None:
        """The finished game as a Match to save, or None if there is nothing to save.

        Nothing to save while the game is running, for games without a clock (a
        match always has a time limit) and for games where nobody made a move.
        """
        end_reason = self._game.end_reason
        if (
            end_reason is None
            or self._ended_utc is None
            or self.minutes is None
            or not self._moves
        ):
            return None
        return Match(
            id=self.id,
            mode=self.mode,
            difficulty=self.difficulty if self.mode is GameMode.COMPUTER else None,
            player_x_id=self.owner_id,
            player_o_id=None,  # the computer, or a guest on the same device
            winner=self._game.winner,
            end_reason=EndReason(end_reason.value),
            time_limit_seconds=round(self.minutes * 60),
            started_at=self._started_utc,
            ended_at=max(self._ended_utc, self._started_utc),
            moves=tuple(self._moves),
        )

    def _bot_turn(self) -> None:
        assert self._bot is not None
        move = self._bot.choose_move(self._game)
        # The time spent thinking comes out of the bot's own clock.
        now = self._now()
        if self._timed_out(now):
            return
        self._play_and_pass_turn(move, now)

    def _play_and_pass_turn(self, move: Move, now: float) -> None:
        self._game.play(move)  # raises IllegalMoveError if the move is not legal
        self._moves.append(move)
        if self._game.is_over:
            self._note_end(now)
        elif self._clock is not None:
            self._clock.switch(now)

    def _timed_out(self, now: float) -> bool:
        if self._clock is None or self._game.is_over:
            return False
        expired = self._clock.tick(now)
        if expired is None:
            return False
        self._game.end_by_timeout(expired)
        self._note_end(now)
        return True

    def _note_end(self, now: float) -> None:
        self._finished_at = now
        self._ended_utc = self._wall_clock()
