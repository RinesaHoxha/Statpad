from fastapi import APIRouter, Request, HTTPException
from app.scrapers.Stadiums.stadiums_scraper import insert_stadiums_into_database
from app.scrapers.Stadiums.stadiums_scraper import scrape_stadiums
from app.database import SessionLocal
from app.models.stadiums import Stadiums
from fastapi.templating import Jinja2Templates
from collections import defaultdict

router = APIRouter(
    prefix='/Stadiums',
    tags=['stadiums']
)

templates = Jinja2Templates(directory="templates")


@router.get("/scrape-and-insert-stadiums")
async def scrape_and_insert():
    db = SessionLocal()
    try:
        scraped_data = scrape_stadiums()
        insert_stadiums_into_database(scraped_data, db)
        return {"message": "Scraping and inserting completed"}

    except Exception as e:
        print(f"Error with scrape_webpage(): {e}")
    finally:
        db.close()


@router.get("/stadiums")
async def show_stadiums(request: Request):
    db = SessionLocal()
    stadiums = db.query(Stadiums).all()
    return stadiums
