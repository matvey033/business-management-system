from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models.user import User
from src.schemas.meeting import MeetingCreate, MeetingRead, MeetingUpdate
from src.auth.auth import current_active_user
from src.services.meetings import MeetingsService

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post("/", response_model=MeetingRead)
async def create_meeting(
    meeting_data: MeetingCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = MeetingsService(session)
    return await service.create_meeting(meeting_data, user)


@router.get("/", response_model=list[MeetingRead])
async def get_my_meetings(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = MeetingsService(session)
    return await service.get_my_meetings(user)


@router.delete("/{meeting_id}")
async def cancel_meeting(
    meeting_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = MeetingsService(session)
    return await service.cancel_meeting(meeting_id, user)


@router.patch("/{meeting_id}", response_model=MeetingRead)
async def update_meeting(
    meeting_id: int,
    meeting_update: MeetingUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    service = MeetingsService(session)
    return await service.update_meeting(meeting_id, meeting_update, user)
