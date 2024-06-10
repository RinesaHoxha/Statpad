from fastapi import APIRouter, HTTPException

from app.database import SessionLocal
from app.models.lineup import Lineup
from app.scrapers.lineup.lineup import scrape_lineup_info_for_teams, insert_lineup_data, delete_all_lineup

router = APIRouter(prefix='/lineup', tags=['lineup'])

@router.get("/scrape")
async def scrape_and_insert_lineup_data():
    try:
        lineup_data = scrape_lineup_info_for_teams()
        delete_all_lineup()
        insert_lineup_data(lineup_data)
        return {"message": "Lineup data scraped and inserted successfully", "data": lineup_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get('/data')
def lineup_data():
    db=SessionLocal()
    lineups=db.query(Lineup).all()
    return lineups

