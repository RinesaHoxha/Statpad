from fastapi import APIRouter, Query
from app.scrapers.Match_data.Top_5 import scrape_and_save_match_data
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/scrape-data',
    tags=['Scrape Data']
)

templates = Jinja2Templates(directory="templates")



@router.get("/")
async def scrape_data_and_save(
    years: list = Query(..., title="List of years", description="Enter the years to scrape data for", min_length=1)
):
    try:
        scrape_and_save_match_data(years)
        return {"message": "Data scraped and saved successfully"}
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}