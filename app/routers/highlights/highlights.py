from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from app.models.highlights import HighlightsDB
from app.scrapers.highlights.highlights import highlights_scraped, insert_data_into_database
from app.scrapers.highlights.highlights_backup import backup_highlights_scraped
from app.database import SessionLocal
from sqlalchemy import desc, func
from app.models.news import News



templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='/highlights',
    tags=['highlights']
)

@router.get("/scrapehighlights")
def scrape_and_save_to_db():
    try:
        scraped_data = highlights_scraped()
        if not scraped_data:
            scraped_data = backup_highlights_scraped()

        db = SessionLocal()
        insert_data_into_database(db, scraped_data)

        return {"message": "Highlights scraped and saved successfully!"}

    except Exception as e:
        return HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/highlights")
def highlights_data(q: str = Query(None)):
    db = SessionLocal()
    if q:
        highlights = db.query(HighlightsDB).filter(HighlightsDB.competition.ilike(f"%{q}%")).all()
    else:
        highlights = db.query(HighlightsDB).all()
    db.close()
    return highlights


@router.get('/view')
def highlights_view(request: Request, q: str = '', page: int = 1, items_per_page: int = 12):
    db = SessionLocal()

    try:
        offset = (page - 1) * items_per_page
        limit = items_per_page

        if q:
            # Filter news based on the search query
            query = db.query(HighlightsDB).filter(HighlightsDB.match_name.ilike(f"%{q}%"))
            hg = query.order_by(desc(func.to_date(HighlightsDB.date, 'DD-MM-YYYY'))).offset(offset).limit(limit).all()
            total_hg_count = query.count()
        else:
            query = db.query(HighlightsDB)
            hg = query.order_by(desc(func.to_date(HighlightsDB.date, 'DD-MM-YYYY'))).offset(offset).limit(limit).all()
            total_hg_count = query.count()
        total_highlights = total_hg_count
        total_pages = (total_highlights + items_per_page - 1) // items_per_page
        page_numbers = range(1, total_pages + 1)
        news = db.query(News).all()

        return templates.TemplateResponse('highlights.html',
                                          {
                                              'request': request,
                                              'hg': hg,
                                              'total_pages': total_pages,
                                              'current_page': page,
                                              'page_numbers': page_numbers,
                                              'news': news
                                          })
    finally:
        db.close()






