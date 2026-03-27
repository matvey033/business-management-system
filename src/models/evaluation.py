from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, ForeignKey, CheckConstraint

from src.database import Base


if TYPE_CHECKING:
    from src.models.task import Task


class Evaluation(Base):
    __tablename__ = "evaluation"

    id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("task.id"), unique=True, nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 5", name="check_score_range"),
    )

    task: Mapped["Task"] = relationship(back_populates="evaluation")
