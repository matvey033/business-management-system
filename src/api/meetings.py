from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.database import get_async_session
from src.models.user import User
from src.models.meeting import Meeting
from src.schemas.meeting import MeetingCreate, MeetingRead
from src.auth.auth import current_active_user

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post("/", response_model=MeetingRead)
async def create_meeting(
    meeting_data: MeetingCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    overlap_query = select(Meeting).where(
        and_(
            Meeting.user_id == user.id,
            Meeting.start_time < meeting_data.end_time,
            Meeting.end_time > meeting_data.start_time,
        )
    )

    result = await session.execute(overlap_query)
    overlapping_meeting = result.scalars().first()

    if overlapping_meeting:
        raise HTTPException(
            status_code=400,
            detail=f"У вас уже запланирована встреча на это время: '{overlapping_meeting.title}'",
        )

    new_meeting = Meeting(
        title=meeting_data.title,
        start_time=meeting_data.start_time,
        end_time=meeting_data.end_time,
        user_id=user.id,
    )

    session.add(new_meeting)
    await session.commit()
    await session.refresh(new_meeting)

    return new_meeting


@router.get("/", response_model=list[MeetingRead])
async def get_my_meetings(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = (
        select(Meeting).where(Meeting.user_id == user.id).order_by(Meeting.start_time)
    )
    result = await session.execute(query)

    return result.scalars().all()
