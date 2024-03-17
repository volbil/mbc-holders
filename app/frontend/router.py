from jinja2_fragments.fastapi import Jinja2Blocks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Request, Depends
from app.database import get_session
from . import service


def display_amount(amount):
    return "{:,}".format(round(amount, 4))


templates = Jinja2Blocks(directory="app/templates")
templates.env.filters["amount"] = display_amount
router = APIRouter()


@router.get("/")
async def home(request: Request, session: AsyncSession = Depends(get_session)):
    addresses = await service.get_richlist(session)
    return templates.TemplateResponse(
        "pages/home.html",
        {
            "request": request,
            "addresses": addresses,
            "page": 1,
        },
    )
