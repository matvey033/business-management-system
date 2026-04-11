from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.team import Team
from src.models.user import User, Role
from src.schemas.team import TeamCreate


class TeamsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_team(self, team_data: TeamCreate) -> Team:
        new_team = Team(name=team_data.name, description=team_data.description)
        self.session.add(new_team)
        try:
            await self.session.commit()
            await self.session.refresh(new_team)
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при создании команды"
            ) from None
        return new_team

    async def join_team(self, join_code: str, user: User) -> dict[str, str]:
        team = (
            await self.session.execute(select(Team).where(Team.join_code == join_code))
        ).scalar_one_or_none()

        if not team:
            raise HTTPException(status_code=404, detail="Команда с таким кодом не найдена")

        user.team_id = team.id
        self.session.add(user)
        try:
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при присоединении к команде"
            ) from None

        return {"message": f"Вы успешно присоединились к команде: {team.name}"}

    async def get_team_users(self, team_id: int) -> list[User]:
        result = await self.session.execute(select(User).where(User.team_id == team_id))
        return result.scalars().all()

    async def kick_user_from_team(self, team_id: int, user_id: int) -> dict[str, str]:
        target_user = (
            await self.session.execute(select(User).where(User.id == user_id))
        ).scalar_one_or_none()

        if not target_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if target_user.team_id != team_id:
            raise HTTPException(
                status_code=400, detail="Пользователь не состоит в этой команде"
            )

        target_user.team_id = None
        self.session.add(target_user)
        try:
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при исключении пользователя из команды"
            ) from None

        return {"message": f"Пользователь {target_user.email} исключен из команды"}

    async def assign_user_role(
        self, team_id: int, user_id: int, role: Role
    ) -> dict[str, str]:
        target_user = (
            await self.session.execute(select(User).where(User.id == user_id))
        ).scalar_one_or_none()

        if not target_user or target_user.team_id != team_id:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден в вашей команде"
            )

        target_user.role = role
        self.session.add(target_user)
        try:
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Ошибка при изменении роли пользователя"
            ) from None

        return {"message": f"Роль пользователя {target_user.email} изменена на {role}"}
