from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.models import Address


async def get_holders_count(session: AsyncSession):
    return await session.scalar(
        select(func.count(Address.id)).filter(Address.balance > 0)
    )


async def get_holders(session: AsyncSession, limit: int, offset: int):
    return await session.scalars(
        select(Address)
        .filter(Address.balance > 0)
        .order_by(desc(Address.balance))
        .limit(limit)
        .offset(offset)
    )
