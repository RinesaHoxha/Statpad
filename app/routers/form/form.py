from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.models.form import FormDB
from app.scrapers.form.form import scrape_form_in_last_matches, insert_data_into_database
from app.database import SessionLocal
from fastapi import HTTPException


router = APIRouter(
    prefix='/form',
    tags=['/form']
)
templates = Jinja2Templates(directory='templates')


@router.get("/scrape")
async def scrape_and_save_form_to_db():
    db = SessionLocal()
    try:
        games_data = scrape_form_in_last_matches()
        insert_data_into_database(games_data)
        return {"message": "Form data scraped and saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/form_data")
def get_form_data():
    db = SessionLocal()
    form_data = db.query(FormDB).all()
    db.close()
    return form_data
