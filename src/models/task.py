import enum
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Enum, ForeignKey, DateTime, CheckConstraint

from src.database import Base

if TYPE_CHECKING:
    from src.models.team import Team
    from src.models.user import User
    from src.models.evaluation import Evaluation
    from src.models.comment import Comment


class TaskStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    done = "done"


class Task(Base):
    __tablename__ = "task"
    __table_args__ = (
        CheckConstraint(
            "status <> 'done' OR assignee_id IS NOT NULL",
            name="check_done_task_requires_assignee",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.open, nullable=False
    )

    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )

    team: Mapped["Team"] = relationship(foreign_keys=[team_id])
    author: Mapped["User"] = relationship(foreign_keys=[author_id])
    assignee: Mapped["User"] = relationship(foreign_keys=[assignee_id])

    evaluation: Mapped["Evaluation"] = relationship(
        back_populates="task", uselist=False
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )

    team: Mapped["Team"] = relationship("Team")
    assignee: Mapped["User"] = relationship("User", foreign_keys=[assignee_id])

    def __str__(self):
        return self.title
