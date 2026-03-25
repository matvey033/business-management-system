from pydantic import BaseModel, ConfigDict


class TeamCreate(BaseModel):
    name: str
    description: str | None = None


class TeamRead(BaseModel):
    id: int
    name: str
    description: str | None
    join_code: str

    model_config = ConfigDict(from_attributes=True)
