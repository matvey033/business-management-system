from pydantic import BaseModel, ConfigDict, Field


class EvaluationCreate(BaseModel):
    score: int = Field(ge=1, le=5, description="Оценка от 1 до 5")
    comment: str | None = None


class EvaluationRead(BaseModel):
    id: int
    score: int
    comment: str | None
    task_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
