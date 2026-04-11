from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models.user import User, Role
from src.schemas.team import TeamCreate, TeamRead
from src.auth.auth import current_active_user
from src.api.dependencies import get_current_admin
from src.schemas.user import UserRead
from src.services.teams import TeamsService

from pydantic import BaseModel


class RoleUpdate(BaseModel):
    role: Role


router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("/", response_model=TeamRead)
async def create_team(
    team_data: TeamCreate,
    user: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_async_session),
):
    service = TeamsService(session)
    return await service.create_team(team_data)


@router.post("/join")
async def join_team(
    join_code: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = TeamsService(session)
    return await service.join_team(join_code, user)


@router.get("/{team_id}/users", response_model=list[UserRead])
async def get_team_users(
    team_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = TeamsService(session)
    return await service.get_team_users(team_id)


@router.post("/{team_id}/kick/{user_id}")
async def kick_user_from_team(
    team_id: int,
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_async_session),
):
    service = TeamsService(session)
    return await service.kick_user_from_team(team_id, user_id)


@router.patch("/{team_id}/role/{user_id}")
async def assign_user_role(
    team_id: int,
    user_id: int,
    role_data: RoleUpdate,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_async_session),
):
    service = TeamsService(session)
    return await service.assign_user_role(team_id, user_id, role_data.role)
