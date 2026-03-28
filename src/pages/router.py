import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Frontend"])

current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(os.path.dirname(current_dir), "templates")

templates = Jinja2Templates(directory=templates_dir)


@router.get("/")
async def get_calendar_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
