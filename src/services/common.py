from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

ModelT = TypeVar("ModelT")


async def get_one_or_none(
    session: AsyncSession, entity: type[ModelT], *filters: ColumnElement[bool]
) -> ModelT | None:
    return (await session.execute(select(entity).where(*filters))).scalar_one_or_none()


async def get_one_or_404(
    session: AsyncSession,
    entity: type[ModelT],
    *filters: ColumnElement[bool],
    detail: str,
) -> ModelT:
    instance = await get_one_or_none(session, entity, *filters)
    if instance is None:
        raise HTTPException(status_code=404, detail=detail)
    return instance
