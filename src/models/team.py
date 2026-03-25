import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text

from src.database import Base


# Функция для генерации случайного кода команды (например: 3f8a9b)
def generate_join_code() -> str:
    return uuid.uuid4().hex[:8]


class Team(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    join_code: Mapped[str] = mapped_column(
        String(20), unique=True, default=generate_join_code, nullable=False
    )

    users: Mapped[list["User"]] = relationship(back_populates="team")
