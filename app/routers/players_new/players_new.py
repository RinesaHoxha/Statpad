from fastapi import APIRouter, HTTPException, Request
from app.models.players_new import Players
from app.scrapers.players_new.players_new import scrape_players, save_player_data_to_db
from app.database import SessionLocal
from fastapi.templating import Jinja2Templates
from app.models.news import News

router = APIRouter(
    prefix='/leagues',
    tags=['leagues']
)

templates = Jinja2Templates(directory="templates")

league_urls = {
    "Champions League": "https://www.transfermarkt.com/uefa-champions-league/scorerliste/pokalwettbewerb/CL",
    "Europa League": "https://transfermarkt.com/europa-league/scorerliste/pokalwettbewerb/EL",
}

@router.get("/scrape-players")
def scrape_and_save_players():
    try:
        db = SessionLocal()

        all_players = []

        for league, url in league_urls.items():
            players = scrape_players(url, league)
            save_player_data_to_db(players, db, league)
            all_players.extend(players)

        db.close()
        return {"message": f"Scraped and saved {len(all_players)} players for all leagues"}

    except Exception as e:
        return HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/players")
def get_players_data(q: str = None):
    db = SessionLocal()

    query = db.query(Players)

    if q:
        query = query.filter(Players.player_name.ilike(f"%{q}%"))

    players_data = query.all()
    db.close()

    return players_data

@router.get("/view")
def players_view(request: Request):
    db = SessionLocal()
    players = db.query(Players).all()
    db.close()
    news = db.query(News).all()
    return templates.TemplateResponse("players.html", {"request": request, "players": players, 'news' : news})
