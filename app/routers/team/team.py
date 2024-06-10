from fastapi import APIRouter, Request, HTTPException
from app.scrapers.team.team import insert_team_into_database
from app.scrapers.team.team import scrape_team
from app.database import SessionLocal
from app.models.team import Team
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/Team',
    tags=['team']
)

templates = Jinja2Templates(directory="templates")


@router.get("/scrape-and-insert-team")
async def scrape_and_insert():
    db = SessionLocal()
    try:
        scraped_data = scrape_team()
        insert_team_into_database(scraped_data, db)
        return {"message": "Scraping and inserting completed"}

    except Exception as e:
        print(f"Error with scrape_team(): {e}")
    finally:
        db.close()


@router.get("/team")
async def show_team(request: Request):
    db = SessionLocal()
    team = db.query(Team).all()
    return team
