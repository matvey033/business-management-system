from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_async_session
from src.models.user import User, Role
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskRead, TaskUpdate
from src.auth.auth import current_active_user
from src.api.dependencies import get_manager_user
from src.models.comment import Comment
from src.schemas.comment import CommentCreate, CommentRead

router = APIRouter(prefix="/tasks", tags=["Tasks"])


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


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Task).where(Task.id == task_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.author_id != user.id and task.assignee_id != user.id:
        raise HTTPException(
            status_code=403, detail="У вас нет прав на редактирование этой задачи"
        )

    update_data = task_update.model_dump(exclude_unset=True)

    if task.author_id != user.id and task.assignee_id == user.id:
        if "status" in update_data:
            task.status = update_data["status"]
        else:
            raise HTTPException(
                status_code=403, detail="Исполнитель может менять только статус задачи"
            )
    else:
        for key, value in update_data.items():
            setattr(task, key, value)

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Task).where(Task.id == task_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.author_id != user.id:
        raise HTTPException(
            status_code=403, detail="Только автор может удалить эту задачу"
        )

    await session.delete(task)
    await session.commit()

    return {"message": "Задача успешно удалена"}


@router.post("/{task_id}/comments", response_model=CommentRead)
async def add_comment(
    task_id: int,
    comment_data: CommentCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Task).where(Task.id == task_id)
    task = (await session.execute(query)).scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    new_comment = Comment(text=comment_data.text, task_id=task.id, user_id=user.id)
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)

    return new_comment


@router.get("/{task_id}/comments", response_model=list[CommentRead])
async def get_comments(
    task_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = (
        select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at)
    )
    result = await session.execute(query)

    return result.scalars().all()
