from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.meeting import Meeting
from src.models.user import User
from src.schemas.meeting import MeetingCreate, MeetingUpdate
from src.services.common import get_one_or_404


class MeetingsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_meeting(self, meeting_data: MeetingCreate, user: User) -> Meeting:
        overlap_query = select(Meeting).where(
            and_(
                Meeting.user_id == user.id,
                Meeting.start_time < meeting_data.end_time.replace(tzinfo=None),
                Meeting.end_time > meeting_data.start_time.replace(tzinfo=None),
            )
        )
        overlapping_meeting = (
            (await self.session.execute(overlap_query)).scalars().first()
        )
        if overlapping_meeting:
            raise HTTPException(
                status_code=400,
                detail=f"У вас уже запланирована встреча на это время: '{overlapping_meeting.title}'",
            )

        new_meeting = Meeting(
            title=meeting_data.title,
            start_time=meeting_data.start_time.replace(tzinfo=None),
            end_time=meeting_data.end_time.replace(tzinfo=None),
            user_id=user.id,
        )

        self.session.add(new_meeting)
        try:
            await self.session.commit()
            await self.session.refresh(new_meeting)
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при создании встречи"
            ) from None
        return new_meeting

    async def get_my_meetings(self, user: User) -> list[Meeting]:
        result = await self.session.execute(
            select(Meeting)
            .where(Meeting.user_id == user.id)
            .order_by(Meeting.start_time)
        )
        return result.scalars().all()

    async def cancel_meeting(self, meeting_id: int, user: User) -> dict[str, str]:
        meeting = await get_one_or_404(
            self.session, Meeting, Meeting.id == meeting_id, detail="Встреча не найдена"
        )
        if meeting.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="Вы можете отменять только свои встречи"
            )

        try:
            await self.session.delete(meeting)
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при отмене встречи"
            ) from None
        return {"message": "Встреча успешно отменена"}

    async def update_meeting(
        self, meeting_id: int, meeting_update: MeetingUpdate, user: User
    ) -> Meeting:
        meeting = await get_one_or_404(
            self.session,
            Meeting,
            Meeting.id == meeting_id,
            Meeting.user_id == user.id,
            detail="Встреча не найдена или нет прав",
        )

        update_data = meeting_update.model_dump(exclude_unset=True)

        if "start_time" in update_data and update_data["start_time"]:
            update_data["start_time"] = update_data["start_time"].replace(tzinfo=None)
        if "end_time" in update_data and update_data["end_time"]:
            update_data["end_time"] = update_data["end_time"].replace(tzinfo=None)

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
                    Meeting.id != meeting_id,
                    Meeting.start_time < new_end,
                    Meeting.end_time > new_start,
                )
            )
            if (await self.session.execute(overlap_query)).scalars().first():
                raise HTTPException(
                    status_code=400, detail="Новое время пересекается с другой встречей"
                )

        for key, value in update_data.items():
            setattr(meeting, key, value)

        self.session.add(meeting)
        try:
            await self.session.commit()
            await self.session.refresh(meeting)
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при обновлении встречи"
            ) from None
        return meeting
