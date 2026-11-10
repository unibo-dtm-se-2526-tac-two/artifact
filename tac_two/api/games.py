"""Routes to play a game: create it, read it, play a move.

All the rules, the clock and the bot live in the domain. This module only turns
HTTP requests into calls to a GameSession and the session back into JSON, and
saves the finished games of logged-in players.
"""

import uuid
from functools import lru_cache
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from tac_two.adapters.game_store import GameStore
from tac_two.adapters.models import UserTable
from tac_two.api.auth import fastapi_users
from tac_two.api.dependencies import get_match_repository
from tac_two.api.game_schemas import (
    ClockOut,
    GameCreate,
    GameState,
    Mark,
    MoveIn,
    MoveOut,
)
from tac_two.domain.ai.factory import BotFactory, Difficulty
from tac_two.domain.game.common import GameOverError, IllegalMoveError, Player
from tac_two.domain.game_session import HUMAN, GameSession
from tac_two.domain.match import GameMode
from tac_two.domain.match_repository import MatchRepository

router = APIRouter(prefix="/api/v1/games", tags=["games"])

# The token is optional: guests can play, but only logged-in players get their
# finished games saved.
optional_user = fastapi_users.current_user(optional=True)


@lru_cache
def get_game_store() -> GameStore:
    return GameStore()


Store = Annotated[GameStore, Depends(get_game_store)]
Repository = Annotated[MatchRepository, Depends(get_match_repository)]
CurrentUser = Annotated[UserTable | None, Depends(optional_user)]


def _mark(player: Player) -> Mark:
    return player.value


def to_state(session: GameSession) -> GameState:
    game = session.game
    clock = session.clock
    boards = game.boards
    over = game.is_over

    winners: list[Literal["X", "O", "draw"] | None] = []
    for board in boards:
        if board.winner is not None:
            winners.append(_mark(board.winner))
        else:
            winners.append("draw" if board.is_draw else None)

    moves = session.moves
    first = len(moves) - 2 if len(moves) >= 2 else 0
    last_moves = [
        MoveOut(
            player="X" if index % 2 == 0 else "O",
            board=move[0],
            cell=move[1],
        )
        for index, move in enumerate(moves[first:], start=first)
    ]

    return GameState(
        id=session.id,
        mode="computer" if session.mode is GameMode.COMPUTER else "local",
        difficulty=session.difficulty.value if session.difficulty else None,
        human_player=_mark(HUMAN) if session.mode is GameMode.COMPUTER else None,
        status="finished" if over else "playing",
        current_player=None if over else _mark(game.current_player),
        forced_board=game.forced_board,
        boards=[[None if c is None else _mark(c) for c in b.cells] for b in boards],
        board_winners=winners,
        winner=_mark(game.winner) if game.winner else None,
        end_reason=game.end_reason.value if game.end_reason else None,
        clock=(
            ClockOut(
                x=clock.remaining(Player.X),
                o=clock.remaining(Player.O),
                active=None if over else _mark(clock.active_player),
            )
            if clock
            else None
        ),
        move_count=len(moves),
        last_moves=last_moves,
    )


def _check_access(session: GameSession | None, user: UserTable | None) -> GameSession:
    if session is None:
        raise HTTPException(status_code=404, detail="Game not found.")
    if session.owner_id is not None and (user is None or user.id != session.owner_id):
        raise HTTPException(
            status_code=403, detail="This game belongs to another player."
        )
    return session


async def _save_if_finished(session: GameSession, repository: MatchRepository) -> None:
    """Save the match once. If saving fails, the next request tries again."""
    if session.recorded or session.owner_id is None:
        return
    match = session.to_match()
    if match is not None:
        await repository.add(match)
        session.recorded = True


@router.post("", response_model=GameState, status_code=201)
async def create_game(body: GameCreate, user: CurrentUser, store: Store) -> GameState:
    mode = GameMode(body.mode)
    difficulty = None
    if mode is GameMode.COMPUTER and body.difficulty is not None:
        difficulty = Difficulty(body.difficulty)
    session = GameSession(
        mode,
        store.now,
        minutes=body.minutes or None,
        bot=BotFactory.create(difficulty) if difficulty else None,
        difficulty=difficulty,
        owner_id=user.id if user else None,
    )
    store.add(session)
    return to_state(session)


@router.get("/{game_id}", response_model=GameState)
async def get_game(
    game_id: uuid.UUID, user: CurrentUser, store: Store, repository: Repository
) -> GameState:
    async with store.open(game_id) as found:
        session = _check_access(found, user)
        session.refresh()  # a game can end just because time went by
        await _save_if_finished(session, repository)
        return to_state(session)


@router.post("/{game_id}/moves", response_model=GameState)
async def play_move(
    game_id: uuid.UUID,
    body: MoveIn,
    user: CurrentUser,
    store: Store,
    repository: Repository,
) -> GameState:
    async with store.open(game_id) as found:
        session = _check_access(found, user)
        try:
            # The bot can think for up to a second: do it in a thread so the
            # other players are not kept waiting.
            await run_in_threadpool(session.play, (body.board, body.cell))
        except GameOverError:
            raise HTTPException(status_code=409, detail="The game is over.") from None
        except IllegalMoveError as error:
            raise HTTPException(status_code=409, detail=str(error)) from None
        await _save_if_finished(session, repository)
        return to_state(session)
