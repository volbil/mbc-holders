from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import Address


async def get_richlist(session: AsyncSession):
    return await session.scalars(
        select(Address).order_by(desc(Address.balance)).limit(100)
    )
