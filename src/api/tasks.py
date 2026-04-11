from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models.user import User
from src.schemas.task import TaskCreate, TaskRead, TaskUpdate
from src.auth.auth import current_active_user
from src.api.dependencies import get_manager_user
from src.schemas.comment import CommentCreate, CommentRead
from src.services.tasks import TasksService


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskRead)
async def create_task(
    task_data: TaskCreate,
    user: User = Depends(get_manager_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = TasksService(session)
    return await service.create_task(task_data, user)


@router.get("/", response_model=list[TaskRead])
async def get_tasks(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = TasksService(session)
    return await service.get_tasks(user)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = TasksService(session)
    return await service.update_task(task_id, task_update, user)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = TasksService(session)
    return await service.delete_task(task_id, user)


@router.post("/{task_id}/comments", response_model=CommentRead)
async def add_comment(
    task_id: int,
    comment_data: CommentCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = TasksService(session)
    return await service.add_comment(task_id, comment_data, user)


@router.get("/{task_id}/comments", response_model=list[CommentRead])
async def get_comments(
    task_id: int,
    _user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = TasksService(session)
    return await service.get_comments(task_id)
