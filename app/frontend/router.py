from .utils import frontend_pagination, pagination
from jinja2_fragments.fastapi import Jinja2Blocks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Request, Depends
from app.database import get_session
from fastapi import Query
from . import service


def display_amount(amount):
    return "{:,}".format(round(amount, 4))


templates = Jinja2Blocks(directory="app/templates")
templates.env.filters["amount"] = display_amount
router = APIRouter()


@router.get("/")
async def home(
    request: Request,
    page: int = Query(gt=0, default=1),
    session: AsyncSession = Depends(get_session),
):
    total = await service.get_holders_count(session)
    limit, offset = pagination(page, size=100)
    addresses = await service.get_holders(session, limit, offset)

    return templates.TemplateResponse(
        "pages/home.html",
        {
            "pagination": frontend_pagination(page, limit, total, "/"),
            "addresses": addresses,
            "request": request,
            "page": page,
        },
    )
