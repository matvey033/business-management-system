from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from src.models.user import User
from src.auth.manager import get_user_manager
from src.auth.auth import auth_backend
from src.schemas.user import UserRead, UserCreate

app = FastAPI(
    title="Business Management System",
    description="Финальный проект EffectiveMobile",
    version="0.1.0",
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)


@app.get("/ping", tags=["Healthcheck"])
async def ping():
    return {"message": "pong!", "status": "success"}
