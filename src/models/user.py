import enum
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, ForeignKey

from src.database import Base


class Role(str, enum.Enum):
    user = "user"
    manager = "manager"
    admin = "admin"


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user, nullable=False)

    team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True)

    team: Mapped["Team"] = relationship(back_populates="users")
