from fastapi import APIRouter, Request, HTTPException
from app.scrapers.live_game_href.live_game_href_scraper import insert_href_into_database
from app.scrapers.live_game_href.live_game_href_scraper import scrape_live_game_href
from app.database import SessionLocal
from app.models.live_game_href import Live_game_href
from fastapi.templating import Jinja2Templates
from app.models.news import News

templates=Jinja2Templates(directory='templates')
router = APIRouter(
    prefix='/game_href',
    tags=['href']
)

templates = Jinja2Templates(directory="templates")


@router.get("/scrape-and-insert-href")
async def scrape_and_insert():
    db = SessionLocal()
    try:
        scraped_data = scrape_live_game_href()
        insert_href_into_database(scraped_data, db)
        return {"message": "Scraping and inserting completed"}

    except Exception as e:
        print(f"Error with scrape_webpage(): {e}")
    finally:
        db.close()


@router.get("/href")
async def show_href(request: Request):
    db = SessionLocal()
    href = db.query(Live_game_href).all()
    news = db.query(News).all()
    return templates.TemplateResponse('matches.html',{'request': request,'live_game_href':href, 'news' : news})
