from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.evaluation import Evaluation
from src.models.task import Task, TaskStatus
from src.models.user import User
from src.schemas.evaluation import EvaluationCreate, EvaluationUpdate
from src.services.common import get_one_or_404, get_one_or_none


class EvaluationsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def evaluate_task(
        self, task_id: int, eval_data: EvaluationCreate, user: User
    ) -> Evaluation:
        task = await get_one_or_none(
            self.session,
            Task,
            Task.id == task_id,
            Task.team_id == user.team_id,
            Task.status == TaskStatus.done,
            Task.assignee_id.is_not(None),
        )
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Задача не найдена или недоступна для оценки",
            )

        existing_eval = await get_one_or_none(
            self.session, Evaluation, Evaluation.task_id == task_id
        )
        if existing_eval:
            raise HTTPException(status_code=400, detail="Эта задача уже оценена")

        new_eval = Evaluation(
            score=eval_data.score,
            comment=eval_data.comment,
            task_id=task.id,
            user_id=task.assignee_id,
        )
        self.session.add(new_eval)
        try:
            await self.session.commit()
            await self.session.refresh(new_eval)
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при создании оценки"
            ) from None
        return new_eval

    async def get_my_average_score(self, user: User) -> dict[str, float | int | str]:
        avg_score = (
            await self.session.execute(
                select(func.avg(Evaluation.score)).where(Evaluation.user_id == user.id)
            )
        ).scalar()
        if avg_score is None:
            return {"average_score": 0}
        return {"average_score": round(avg_score, 2)}

    async def update_evaluation(
        self, eval_id: int, eval_update: EvaluationUpdate
    ) -> Evaluation:
        evaluation = await get_one_or_404(
            self.session,
            Evaluation,
            Evaluation.id == eval_id,
            detail="Оценка не найдена",
        )

        update_data = eval_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(evaluation, key, value)

        self.session.add(evaluation)
        try:
            await self.session.commit()
            await self.session.refresh(evaluation)
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при обновлении оценки"
            ) from None
        return evaluation

    async def delete_evaluation(self, eval_id: int) -> dict[str, str]:
        evaluation = await get_one_or_404(
            self.session,
            Evaluation,
            Evaluation.id == eval_id,
            detail="Оценка не найдена",
        )

        try:
            await self.session.delete(evaluation)
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при удалении оценки"
            ) from None
        return {"message": "Оценка удалена"}
