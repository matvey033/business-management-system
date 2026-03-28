from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.database import get_async_session
from src.models.user import User
from src.models.meeting import Meeting
from src.schemas.meeting import MeetingCreate, MeetingRead, MeetingUpdate
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


@router.delete("/{meeting_id}")
async def cancel_meeting(
    meeting_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Meeting).where(Meeting.id == meeting_id)
    result = await session.execute(query)
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Встреча не найдена")

    if meeting.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="Вы можете отменять только свои встречи"
        )

    await session.delete(meeting)
    await session.commit()

    return {"message": "Встреча успешно отменена"}


@router.patch("/{meeting_id}", response_model=MeetingRead)
async def update_meeting(
    meeting_id: int,
    meeting_update: MeetingUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Meeting).where(Meeting.id == meeting_id)
    meeting = (await session.execute(query)).scalar_one_or_none()

    if not meeting or meeting.user_id != user.id:
        raise HTTPException(status_code=404, detail="Встреча не найдена или нет прав")

    update_data = meeting_update.model_dump(exclude_unset=True)

    new_start = update_data.get("start_time", meeting.start_time)
    new_end = update_data.get("end_time", meeting.end_time)

    if new_start >= new_end:
        raise HTTPException(
            status_code=400, detail="Конец встречи должен быть позже начала"
        )

    if "start_time" in update_data or "end_time" in update_data:
        overlap_query = select(Meeting).where(
            and_(
                Meeting.user_id == user.id,
                Meeting.id != meeting_id,  # Не сравниваем с самой собой!
                Meeting.start_time < new_end,
                Meeting.end_time > new_start,
            )
        )
        if (await session.execute(overlap_query)).scalars().first():
            raise HTTPException(
                status_code=400, detail="Новое время пересекается с другой встречей"
            )

    for key, value in update_data.items():
        setattr(meeting, key, value)

    session.add(meeting)
    await session.commit()
    await session.refresh(meeting)
    return meeting
