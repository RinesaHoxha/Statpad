from fastapi import APIRouter, Request
from app.scrapers.livestream_links.primary_site import scrape_webpage, insert_links_into_database
from app.scrapers.livestream_links.backup_site import insert_links_into_database_backup
from app.scrapers.livestream_links.backup_site import scrape_and_store_links
from app.database import SessionLocal
from app.models.livestream_links import Livestream_links
from fastapi.templating import Jinja2Templates
from collections import defaultdict
from app.models.news import News



router = APIRouter(
    prefix='/livestream',
    tags=['Livestream_links']
)

templates = Jinja2Templates(directory="templates")
@router.get("/scrape-and-insert")
async def scrape_and_insert():
    db = SessionLocal()

    try:
        # Try scrape_webpage() first
        extracted_matches = scrape_webpage()
        insert_links_into_database(extracted_matches, db)
        return extracted_matches
    except Exception as e:
        print(f"Error with scrape_webpage(): {e}")

        # If scrape_webpage() fails, fall back to scrape_and_store_links() and insert_links_into_database_backup()
        try:
            extracted_matches_backup = scrape_and_store_links()
            insert_links_into_database_backup(extracted_matches_backup, db)
            return extracted_matches_backup
        except Exception as e_backup:
            print(f"Error with scrape_and_store_links(): {e_backup}")

    return {"message": "Scraping and inserting completed"}
#ndreqe qeto posht
@router.get("/links")
async def show_livestream_links(request: Request):
    db = SessionLocal()
    matches = db.query(Livestream_links).all()

    # Sort matches by time, with smaller times coming first
    matches.sort(key=lambda match: match.time)

    # Group matches with the same match name
    match_groups = defaultdict(list)
    for match in matches:
        match_groups[match.match].append(match)
    news = db.query(News).all()
    return templates.TemplateResponse("livestreams.html", {"request": request, "match_groups": match_groups, 'news' : news})



