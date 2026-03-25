from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_async_session
from src.models.user import User, Role
from src.models.team import Team
from src.schemas.team import TeamCreate, TeamRead
from src.auth.auth import current_active_user

router = APIRouter(prefix="/teams", tags=["Teams"])


async def get_current_admin(user: User = Depends(current_active_user)):
    if user.role != Role.admin:
        raise HTTPException(
            status_code=403, detail="Только администратор может выполнять это действие"
        )
    return user


@router.post("/", response_model=TeamRead)
async def create_team(
    team_data: TeamCreate,
    user: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_async_session),
):
    new_team = Team(name=team_data.name, description=team_data.description)

    session.add(new_team)
    await session.commit()
    await session.refresh(new_team)

    return new_team


@router.post("/join")
async def join_team(
    join_code: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Team).where(Team.join_code == join_code)
    result = await session.execute(query)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Команда с таким кодом не найдена")

    user.team_id = team.id
    session.add(user)
    await session.commit()

    return {"message": f"Вы успешно присоединились к команде: {team.name}"}
