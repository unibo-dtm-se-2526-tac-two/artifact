from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Base is the mother class and it's used by Alembic to know which tables exist.
class Base(DeclarativeBase):
    pass


# UserTable is the User table. It takes from SQLAlchemyBaseUserTableUUID all the attributes (columns
# id, email, hashed_password, is_active, is_superuser and is_verified). We add only the username, which must be unique.
class UserTable(SQLAlchemyBaseUserTableUUID, Base):
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
