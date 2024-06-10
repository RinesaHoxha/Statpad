from fastapi import APIRouter, Request
from app.scrapers.team_next_clash.team_next_clash import insert_nextmatches_into_database, scrape_nextmatches, \
    delete_all_nextmatches
from app.database import SessionLocal
from app.models.team_next_clash import NextMatches
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/NextMatches',
    tags=['nextmatches']
)

templates = Jinja2Templates(directory="templates")

@router.get("/scrape-and-insert-nextmatches")
async def scrape_and_insert_nextmatches():
    db = SessionLocal()
    try:
        scraped_data = scrape_nextmatches()
        delete_all_nextmatches(db)
        insert_nextmatches_into_database(scraped_data, db)
        return {"message": "Scraping and inserting completed"}
    except Exception as e:
        return {"error": f"Error with scrape_nextmatches(): {str(e)}"}
    finally:
        db.close()

@router.get("/nextmatches")
async def show_nextmatches(request: Request):
    db = SessionLocal()
    nextmatches = db.query(NextMatches).all()
    return nextmatches
