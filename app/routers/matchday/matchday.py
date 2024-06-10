from fastapi import APIRouter, Request, HTTPException
from app.scrapers.matchday.matchday_scraper import insert_matchday_into_database
from app.scrapers.matchday.matchday_scraper import scrape_matchday
from app.database import SessionLocal
from app.models.matchday import Matchday
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/Matchday',
    tags=['matchday']
)

templates = Jinja2Templates(directory="templates")


@router.get("/scrape-and-insert-matchday")
async def scrape_and_insert():
    db = SessionLocal()
    try:
        scraped_data = scrape_matchday()
        insert_matchday_into_database(scraped_data, db)
        return {"message": "Scraping and inserting completed"}

    except Exception as e:
        print(f"Error with scrape_webpage(): {e}")
    finally:
        db.close()


@router.get("/matchday")
async def show_matchday(request: Request):
    db = SessionLocal()
    matchday = db.query(Matchday).all()
    return matchday
