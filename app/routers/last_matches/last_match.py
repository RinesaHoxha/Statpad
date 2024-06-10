from fastapi import APIRouter, Request
from app.scrapers.last_matches.last_match import scrape_lastmatches,insert_lastmatches_into_database
from app.database import SessionLocal
from app.models.last_match import LastMatches
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/LastMatches',
    tags=['lastmatches']
)

templates = Jinja2Templates(directory="templates")

@router.get("/scrape-and-insert")
async def scrape_and_insert():
    db = SessionLocal()
    try:
        scraped_data = scrape_lastmatches()
        insert_lastmatches_into_database(scraped_data, db)
        return {"message": "Scraping and inserting completed"}
    except Exception as e:
        print(f"Error with scrape_and_insert(): {e}")
    finally:
        db.close()

@router.get("/list")
async def show_lastmatches(request: Request):
    db = SessionLocal()
    lastmatches = db.query(LastMatches).all()
    return lastmatches
