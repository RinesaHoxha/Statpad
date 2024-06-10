from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.models.coaches import CoachesDB
from app.scrapers.coaches.coaches import get_coaches_list, insert_coach_data_into_database
from app.database import SessionLocal
from fastapi import HTTPException
from app.models.news import News

router = APIRouter(
    prefix='/coaches',
    tags=['coaches']
)
templates = Jinja2Templates(directory='templates')

@router.get("/scrape")
async def scrape_and_save_to_db():
    db = SessionLocal()

    try:
        scraped_data = get_coaches_list()
        insert_coach_data_into_database(scraped_data)
        return {"message": "Coaches data scraped and saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get('/coaches_data')
def get_coaches_data():
    db = SessionLocal()
    coaches_data = db.query(CoachesDB).all()
    db.close()
    return coaches_data

@router.get('/view')
def view_coaches_data(request: Request):
    db = SessionLocal()
    coaches_data = db.query(CoachesDB).all()

    news = db.query(News).all()
    return templates.TemplateResponse('coaches.html', {
        'request': request,
        'coaches_data': coaches_data,
        'news': news
    })
