import uuid
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Base is the mother class and it's used by Alembic to know which tables exist.
class Base(DeclarativeBase):
    pass


# UserTable is the User table. It takes from SQLAlchemyBaseUserTableUUID all the attributes (columns
# id, email, hashed_password, is_active, is_superuser and is_verified). We add only the username, which must be unique.
class UserTable(SQLAlchemyBaseUserTableUUID, Base):
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)


class MatchTable(Base):
    __tablename__ = "match"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    mode: Mapped[str] = mapped_column(String(20))
    difficulty: Mapped[str | None] = mapped_column(String(20))
    player_x_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), index=True
    )
    player_o_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), index=True
    )
    winner: Mapped[str | None] = mapped_column(String(1))
    end_reason: Mapped[str] = mapped_column(String(20))
    time_limit_seconds: Mapped[int]
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    moves: Mapped[list[list[int]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql")
    )
