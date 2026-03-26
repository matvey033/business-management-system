from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_async_session
from src.models.user import User, Role
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskRead
from src.auth.auth import current_active_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


async def get_manager_user(user: User = Depends(current_active_user)):
    if user.role not in [Role.manager, Role.admin]:
        raise HTTPException(
            status_code=403, detail="Только руководитель может управлять задачами"
        )
    return user


@router.post("/", response_model=TaskRead)
async def create_task(
    task_data: TaskCreate,
    user: User = Depends(get_manager_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.team_id:
        raise HTTPException(
            status_code=400, detail="Сначала присоединитесь к команде или создайте её"
        )

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        deadline=task_data.deadline,
        team_id=user.team_id,
        author_id=user.id,
        assignee_id=task_data.assignee_id,
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return new_task


@router.get("/", response_model=list[TaskRead])
async def get_tasks(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.team_id:
        return []

    query = select(Task).where(Task.team_id == user.team_id)
    result = await session.execute(query)

    return result.scalars().all()
