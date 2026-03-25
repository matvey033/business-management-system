import enum
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum

from src.database import Base


class Role(str, enum.Enum):
    user = "user"
    manager = "manager"
    admin = "admin"


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user, nullable=False)
