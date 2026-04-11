from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models.user import User
from src.schemas.evaluation import EvaluationCreate, EvaluationRead, EvaluationUpdate
from src.auth.auth import current_active_user
from src.api.dependencies import get_manager_user
from src.services.evaluations import EvaluationsService

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post("/task/{task_id}", response_model=EvaluationRead)
async def evaluate_task(
    task_id: int,
    eval_data: EvaluationCreate,
    user: User = Depends(get_manager_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = EvaluationsService(session)
    return await service.evaluate_task(task_id, eval_data, user)


@router.get("/my-average")
async def get_my_average_score(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = EvaluationsService(session)
    return await service.get_my_average_score(user)


@router.patch("/{eval_id}", response_model=EvaluationRead)
async def update_evaluation(
    eval_id: int,
    eval_update: EvaluationUpdate,
    _user: User = Depends(get_manager_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = EvaluationsService(session)
    return await service.update_evaluation(eval_id, eval_update)


@router.delete("/{eval_id}")
async def delete_evaluation(
    eval_id: int,
    _user: User = Depends(get_manager_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = EvaluationsService(session)
    return await service.delete_evaluation(eval_id)
