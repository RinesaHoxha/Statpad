from fastapi import APIRouter, Request, HTTPException, Depends

from app.models.stadiums_info import Stadiumsinfo, StadiumsinfoModel
from app.scrapers.stadium_info.stadiumsinfo_scraper import insert_stadiumsinfo_into_database
from app.scrapers.stadium_info.stadiumsinfo_scraper import scrape_stadiums
from app.database import SessionLocal, get_db
from app.models.stadiums import Stadiums
from fastapi.templating import Jinja2Templates
from collections import defaultdict

router = APIRouter(
    prefix='/Stadiumsinfo',
    tags=['stadiumsinfo']
)

templates = Jinja2Templates(directory="templates")


@router.get("/scrape_and_insert", response_model=list[StadiumsinfoModel])
def scrape_and_insert_stadiums(session: SessionLocal = Depends(get_db)):
    data_list = scrape_stadiums()  # Assuming you have imported the scrape_stadiums function

    for item in data_list:
        new_stadium = Stadiumsinfo(
            stadium_name=item["stadium_name"],
            image=item["image"],
            city=item["city"],
            address=item["address"],
            construction_date=item["construction_date"],
            capacity=item["capacity"],
            size=item["size"],
            grass_type=item["grass_type"],
            phone=item["phone"],
            fax=item["fax"],
            team=item["team"]
        )
        session.add(new_stadium)

    session.commit()
    return data_list

@router.get("/stadiums")
async def show_stadiums(request: Request):
    db = SessionLocal()
    stadiums = db.query(Stadiums).all()
    return stadiums
