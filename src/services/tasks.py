from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment
from src.models.task import Task
from src.models.user import User
from src.schemas.comment import CommentCreate
from src.schemas.task import TaskCreate, TaskUpdate
from src.services.common import get_one_or_404


class TasksService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task_data: TaskCreate, user: User) -> Task:
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

        self.session.add(new_task)
        try:
            await self.session.commit()
            await self.session.refresh(new_task)
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Ошибка при создании задачи") from None
        return new_task

    async def get_tasks(self, user: User) -> list[Task]:
        if not user.team_id:
            return []

        result = await self.session.execute(select(Task).where(Task.team_id == user.team_id))
        return result.scalars().all()

    async def update_task(self, task_id: int, task_update: TaskUpdate, user: User) -> Task:
        task = await get_one_or_404(
            self.session, Task, Task.id == task_id, detail="Задача не найдена"
        )

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

        self.session.add(task)
        try:
            await self.session.commit()
            await self.session.refresh(task)
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Ошибка при обновлении задачи") from None
        return task

    async def delete_task(self, task_id: int, user: User) -> dict[str, str]:
        task = await get_one_or_404(
            self.session, Task, Task.id == task_id, detail="Задача не найдена"
        )
        if task.author_id != user.id:
            raise HTTPException(
                status_code=403, detail="Только автор может удалить эту задачу"
            )

        try:
            await self.session.delete(task)
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Ошибка при удалении задачи") from None
        return {"message": "Задача успешно удалена"}

    async def add_comment(
        self, task_id: int, comment_data: CommentCreate, user: User
    ) -> Comment:
        task = await get_one_or_404(
            self.session, Task, Task.id == task_id, detail="Задача не найдена"
        )

        new_comment = Comment(text=comment_data.text, task_id=task.id, user_id=user.id)
        self.session.add(new_comment)
        try:
            await self.session.commit()
            await self.session.refresh(new_comment)
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при добавлении комментария"
            ) from None
        return new_comment

    async def get_comments(self, task_id: int) -> list[Comment]:
        result = await self.session.execute(
            select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at)
        )
        return result.scalars().all()
