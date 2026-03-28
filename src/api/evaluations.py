from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.database import get_async_session
from src.models.user import User, Role
from src.models.task import Task, TaskStatus
from src.models.evaluation import Evaluation
from src.schemas.evaluation import EvaluationCreate, EvaluationRead, EvaluationUpdate
from src.auth.auth import current_active_user
from src.api.dependencies import get_manager_user

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post("/task/{task_id}", response_model=EvaluationRead)
async def evaluate_task(
    task_id: int,
    eval_data: EvaluationCreate,
    user: User = Depends(get_manager_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Task).where(Task.id == task_id)
    task = (await session.execute(query)).scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.status != TaskStatus.done:
        raise HTTPException(
            status_code=400,
            detail="Можно оценить только завершенную задачу (статус 'done')",
        )

    if task.team_id != user.team_id:
        raise HTTPException(
            status_code=403, detail="Нельзя оценивать задачи чужой команды"
        )

    if not task.assignee_id:
        raise HTTPException(
            status_code=400, detail="У задачи нет исполнителя для оценки"
        )

    existing_eval = await session.execute(
        select(Evaluation).where(Evaluation.task_id == task_id)
    )
    if existing_eval.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Эта задача уже оценена")

    new_eval = Evaluation(
        score=eval_data.score,
        comment=eval_data.comment,
        task_id=task.id,
        user_id=task.assignee_id,  # Оценка идет в копилку исполнителя
    )
    session.add(new_eval)
    await session.commit()
    await session.refresh(new_eval)

    return new_eval


@router.get("/my-average")
async def get_my_average_score(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(func.avg(Evaluation.score)).where(Evaluation.user_id == user.id)
    result = await session.execute(query)
    avg_score = result.scalar()

    if avg_score is None:
        return {"average_score": 0, "message": "У вас пока нет оценок"}

    return {"average_score": round(avg_score, 2)}


@router.patch("/{eval_id}", response_model=EvaluationRead)
async def update_evaluation(
    eval_id: int,
    eval_update: EvaluationUpdate,
    user: User = Depends(get_manager_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Evaluation).where(Evaluation.id == eval_id)
    evaluation = (await session.execute(query)).scalar_one_or_none()

    if not evaluation:
        raise HTTPException(status_code=404, detail="Оценка не найдена")

    update_data = eval_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(evaluation, key, value)

    session.add(evaluation)
    await session.commit()
    await session.refresh(evaluation)
    return evaluation


@router.delete("/{eval_id}")
async def delete_evaluation(
    eval_id: int,
    user: User = Depends(get_manager_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Evaluation).where(Evaluation.id == eval_id)
    evaluation = (await session.execute(query)).scalar_one_or_none()

    if not evaluation:
        raise HTTPException(status_code=404, detail="Оценка не найдена")

    await session.delete(evaluation)
    await session.commit()
    return {"message": "Оценка удалена"}
