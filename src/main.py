from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.auth import fastapi_users, auth_backend
from src.schemas.user import UserRead, UserCreate, UserUpdate

from src.api.teams import router as teams_router
from src.api.tasks import router as tasks_router
from src.api.evaluations import router as evaluations_router
from src.api.meetings import router as meetings_router
from src.pages.router import router as pages_router

app = FastAPI(
    title="Business Management System",
    description="Финальный проект EffectiveMobile",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["Users"],
)

app.include_router(teams_router)
app.include_router(tasks_router)
app.include_router(evaluations_router)
app.include_router(meetings_router)
app.include_router(pages_router)
