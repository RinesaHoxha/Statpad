from fastapi import APIRouter, Query,Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func

from app.models.news import News
from app.scrapers.news.news import scrape_sport_articles, save_to_db
from app.database import SessionLocal

router = APIRouter(
    prefix='/sportnews',
    tags=['sportnews']
)
templates=Jinja2Templates(directory='templates')


@router.get("/scrape")
async def scrape():
    db = SessionLocal()
    try:
        scraped_data = scrape_sport_articles()
        save_to_db(scraped_data, db)
        return {"message": "Data scraped and saved successfully"}
    except Exception as e:
        print(f"Exception during scraping or database operation: {str(e)}")
    finally:
        db.close()


@router.get("/newsdata")
def read_news(q:str=Query(None)):
    db = SessionLocal()
    if q:
        news=db.query(News).filter(News.title.ilike(f"%{q}%")).all()
    else:
        news = db.query(News).all()
    db.close()
    return news

@router.get('/view')
async def view_news(request: Request, q: str = '', page: int = 1, items_per_page: int = 9):
    db = SessionLocal()

    try:
        offset = (page - 1) * items_per_page
        limit = items_per_page

        query = db.query(News)

        if q:
            query = query.filter(News.title.ilike(f"%{q}%") | News.context.ilike(f"%{q}%"))

        news = query.order_by(desc(func.to_date(News.dateposted, 'DD-MM-YYYY'))).offset(offset).limit(limit).all()
        total_news_count = query.count()

        total_pages = (total_news_count + items_per_page - 1) // items_per_page
        page_numbers = list(range(1, total_pages + 1))

        return templates.TemplateResponse('news.html', {
            'request': request,
            'news': news,
            'page_numbers': page_numbers,
            'current_page': page,
            'total_pages': total_pages
        })
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    finally:
        db.close()
