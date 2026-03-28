from fastapi_users import schemas
from pydantic import ConfigDict, model_validator

from src.models.user import Role


class UserRead(schemas.BaseUser[int]):
    role: Role

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    role: Role = Role.user

    # @model_validator(mode="after")
    # def validate_password(self) -> "UserCreate":
    #     if len(self.password) < 8:
    #         raise ValueError("Пароль должен содержать не менее 8 символов")
    #     return self


class UserUpdate(schemas.BaseUserUpdate):
    role: Role | None = None
