from fastapi_users import schemas
from pydantic import ConfigDict

from src.models.user import Role


class UserRead(schemas.BaseUser[int]):
    role: Role

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    role: Role = Role.user


class UserUpdate(schemas.BaseUserUpdate):
    role: Role | None = None
