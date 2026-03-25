from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    deadline: datetime | None = None
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    deadline: datetime | None = None
    assignee_id: int | None = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    deadline: datetime | None
    team_id: int
    author_id: int
    assignee_id: int | None

    model_config = ConfigDict(from_attributes=True)
