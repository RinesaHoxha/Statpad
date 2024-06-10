from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from app.models.bet import Bets
from app.scrapers.bets.bet import scrape_bet, save_to_db, delete_all_bets
from app.database import SessionLocal
from app.models.news import News

router = APIRouter(
    prefix='/bets',
    tags=['bets']
)
templates = Jinja2Templates(directory='templates')


@router.get("/scrapebets")
def scrape_and_save_to_db():
    try:
        scraped_data = scrape_bet()
        db = SessionLocal()
        delete_all_bets()
        save_to_db(scraped_data['bets'], db)

        return {"message": scraped_data}

    except Exception as e:
        return HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/betsdata")
def bets_data(q: str = Query(None)):
    db = SessionLocal()
    if q:
        bets = db.query(Bets).filter(Bets.liga.ilike(f"%{q}%")).all()
    else:
        bets = db.query(Bets).all()
    db.close()
    return bets

@router.get('/view')
def view_bets(request: Request, q: str = '', page: int = 1, items_per_page: int = 15):
    db = SessionLocal()

    offset = (page - 1) * items_per_page
    limit = items_per_page

    # Show all bets
    query = db.query(Bets)

    if q:
        query = query.filter(Bets.team1.ilike(f"%{q}%") | Bets.team2.ilike(f"%{q}%") | Bets.liga.ilike(f"%{q}%"))

    total_bets_count = query.count()

    total_pages = (total_bets_count + items_per_page - 1) // items_per_page

    page_numbers = list(range(1, total_pages + 1))

    bets = query.slice(offset, offset + limit).all()
    news = db.query(News).all()

    return templates.TemplateResponse('bets.html', {
        'request': request,
        'query': query,
        'bets': bets,
        'page_numbers': page_numbers,
        'current_page': page,
        'total_pages': total_pages,
        'news': news
    })