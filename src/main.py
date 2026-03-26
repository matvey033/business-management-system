from fastapi import FastAPI

from src.auth.auth import fastapi_users, auth_backend
from src.schemas.user import UserRead, UserCreate

from src.api.teams import router as teams_router
from src.api.tasks import router as tasks_router

app = FastAPI(
    title="Business Management System",
    description="Финальный проект EffectiveMobile",
    version="0.1.0",
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

app.include_router(teams_router)
app.include_router(tasks_router)


@app.get("/ping", tags=["Healthcheck"])
async def ping():
    return {"message": "pong!", "status": "success"}
