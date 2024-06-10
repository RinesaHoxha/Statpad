from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from app.models.highlights import HighlightsDB
from app.database import SessionLocal
from app.models.news import News

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get('/highlights/{video_id}')
def highlight_detail(request: Request, video_id: str):
    db = SessionLocal()

    try:
        hg = db.query(HighlightsDB).filter(HighlightsDB.match_name == video_id).all()

        if not hg:
            raise HTTPException(status_code=404, detail="Highlights not found")

        news = db.query(News).all()
        highlights = db.query(HighlightsDB).all()

        return templates.TemplateResponse('highlights_pages.html',
                                          {
                                              'request': request,
                                              'hg': hg,
                                              'news': news,
                                              'highlights': highlights
                                          })
    finally:
        db.close()