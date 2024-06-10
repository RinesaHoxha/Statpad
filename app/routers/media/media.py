from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.models.media import MediaDB  # Import your Media model
from app.scrapers.media.media import get_media_links_with_text, insert_media_data_into_database
from app.database import SessionLocal
from fastapi import HTTPException
from app.models.news import News

router = APIRouter(
    prefix='/media',
    tags=['media']
)
templates = Jinja2Templates(directory='templates')

@router.get("/scrape")
async def scrape_and_save_media_to_db():
    db = SessionLocal()

    try:
        media_data = get_media_links_with_text()
        insert_media_data_into_database(media_data)
        return {"message": "Media data scraped and saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get('/media_data')
def get_media_data():
    db = SessionLocal()
    media_data = db.query(MediaDB).all()
    db.close()
    return media_data

@router.get('/view')
def view_media_data(request: Request):
    db = SessionLocal()
    media_data = db.query(MediaDB).all()
    news = db.query(News).all()
    return templates.TemplateResponse('media.html', {
        'request': request,
        'media_data': media_data,
        'news': news
    })
