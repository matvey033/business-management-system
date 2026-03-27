from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator


class MeetingCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def check_time_logic(self) -> "MeetingCreate":
        if self.start_time >= self.end_time:
            raise ValueError("Время окончания должно быть позже времени начала!")
        return self


class MeetingRead(BaseModel):
    id: int
    title: str
    start_time: datetime
    end_time: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)
