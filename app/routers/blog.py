from fastapi import APIRouter,  Request
from app.models.news import News
from app.database import SessionLocal
from fastapi.templating import Jinja2Templates


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/blog/")
async def blog_view(request: Request):
    db = SessionLocal()
    return templates.TemplateResponse("social.html", {"request": request})