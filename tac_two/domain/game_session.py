"""A game being played: the rules, the chess clock and, optionally, a bot.

This is where the pieces of the engine meet. It stays pure Python (no FastAPI,
no database) and never reads the system time by itself: the caller gives it a
time source, so tests are instant and the server is the only one deciding what
time it is.

Nothing runs in the background. In computer mode the bot answers after a short
wait (`bot_delay`), like a person thinking: its clock runs during the wait. The
session works out what happened when somebody asks: every public method first
catches up with the time that went by.
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
        bot_delay: float = 0.0,
    ) -> None:
        """`minutes` is the time of each player; None or 0 means no clock.

        `now` measures durations (seconds, any monotonic source); `wall_clock`
        gives the real date and time, only used to date the saved match.
        `bot_delay` is how many seconds the bot waits before answering. Its clock
        runs while it waits, as if it were thinking.
        """
        if mode is GameMode.ONLINE:
            raise ValueError("online games are not played with a GameSession")
        if mode is GameMode.COMPUTER and (bot is None or difficulty is None):
            raise ValueError("computer mode needs a bot and a difficulty")
        if bot_delay < 0:
            raise ValueError("bot_delay cannot be negative")
        self.id = uuid.uuid4()
        self.mode = mode
        self.difficulty = difficulty
        self.owner_id = owner_id
        self.minutes = minutes or None
        self.recorded = False  # set once the match has been saved
        self._now = now
        self._wall_clock = wall_clock
        self._bot = bot
        self._bot_delay = bot_delay
        self._bot_due: float | None = None  # when the bot answers (None: not waiting)
        self._paused = False
        self._paused_at = 0.0
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

    @property
    def paused(self) -> bool:
        """True while a player has paused the game."""
        return self._paused

    @property
    def bot_move_in(self) -> float | None:
        """Seconds before the bot answers, or None if it is not waiting."""
        if self._bot_due is None or self._game.is_over:
            return None
        if self._paused:
            return self._bot_due - self._paused_at
        return max(0.0, self._bot_due - self._now())

    def refresh(self) -> None:
        """Bring the game up to date: the bot may have to answer, or somebody
        may have run out of time."""
        self._catch_up()

    def pause(self) -> None:
        """Stop the clock and the bot's wait until `resume`.

        If somebody has just run out of time the game ends instead.
        """
        if self._game.is_over:
            raise GameOverError("the game is already over")
        self._catch_up()
        if self._game.is_over or self._paused:
            return
        now = self._now()
        if self._clock is not None:
            self._clock.pause(now)
        self._paused = True
        self._paused_at = now

    def resume(self) -> None:
        """Start again after a pause. The time in pause is charged to nobody."""
        if self._game.is_over:
            raise GameOverError("the game is already over")
        if not self._paused:
            return
        now = self._now()
        if self._bot_due is not None:
            # The bot's wait goes on from where it stopped.
            self._bot_due += now - self._paused_at
        if self._clock is not None:
            self._clock.resume(now)
        self._paused = False

    def play(self, move: Move) -> None:
        """Play a move for the current player.

        In computer mode the bot answers after `bot_delay` seconds (at once if
        the delay is 0). If the player's time is already up, the move is not
        played and the game ends with a timeout instead.
        """
        if self._game.is_over:
            raise GameOverError("the game is already over")
        if self._paused:
            raise IllegalMoveError("the game is paused")
        self._catch_up()
        if self._game.is_over:
            return
        if self.mode is GameMode.COMPUTER and self._game.current_player is not HUMAN:
            raise IllegalMoveError("it is not your turn")
        now = self._now()
        self._play_and_pass_turn(move, now)
        if self.mode is GameMode.COMPUTER and not self._game.is_over:
            self._wait_for_bot(now)

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

    def _catch_up(self) -> None:
        """Do what the passing of time requires: the bot answers if its wait is
        over, then the active player may run out of time."""
        if self._game.is_over or self._paused:
            return
        now = self._now()
        due = self._bot_due
        if due is not None and due <= now:
            self._bot_due = None
            if self._timed_out(due):  # its time ran out while it was waiting
                return
            self._bot_turn(due)
            now = self._now()
        self._timed_out(now)

    def _wait_for_bot(self, now: float) -> None:
        if self._bot_delay > 0:
            self._bot_due = now + self._bot_delay  # its clock is already running
        else:
            self._bot_turn(now)

    def _bot_turn(self, start: float) -> None:
        """The bot thinks and plays; `start` is when its turn began."""
        assert self._bot is not None
        thinking_from = self._now()
        move = self._bot.choose_move(self._game)
        # The time spent thinking comes out of the bot's own clock.
        moved_at = start + (self._now() - thinking_from)
        if self._timed_out(moved_at):
            return
        self._play_and_pass_turn(move, moved_at)

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
