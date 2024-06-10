import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from app.routers import blog
from app.routers.highlights_pages import highlights_pages
from app.routers.user import user_routes
from app.routers.matches import matches
from app.routers.scrapers_schedulers import scheduler
from app.routers.bets import bet
from app.routers.news import news
from app.routers.players import players
from app.routers.livestream_links import livestream
from app.routers.highlights import highlights
from app.routers.standings import standing
from app.routers.coaches import coaches
from app.routers.media import media
from app.routers.stadiums import stadiums
from app.routers.team import team
from app.routers.matchday import matchday
from app.routers.form import form
from app.routers.live_game_href import live_game_href
from app.routers.lineup import lineup
from app.routers.myteam import myteam
from app.routers.last_matches import last_match
from app.routers.team_next_clash import team_next_clash
from app.routers.stadium_info import stadiums_info
from app.routers.players_new import players_new
from app.routers.Predictions import Predictions
from app.routers.contact import contact
from app.routers.Match_data import match_data_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(Predictions.router)
app.include_router(user_routes.router, prefix="/api")
app.include_router(players.router)
app.include_router(bet.router)
app.include_router(news.router)
app.include_router(standing.router)
app.include_router(livestream.router)
app.include_router(highlights.router)
app.include_router(matches.router)
app.include_router(coaches.router)
app.include_router(media.router)
app.include_router(stadiums.router)
app.include_router(matchday.router)
app.include_router(form.router)
app.include_router(team.router)
app.include_router(lineup.router)
app.include_router(myteam.router)
app.include_router(last_match.router)
app.include_router(team_next_clash.router)
app.include_router(live_game_href.router)
app.include_router(blog.router)
app.include_router(highlights_pages.router)
app.include_router(stadiums_info.router)
app.include_router(players_new.router)
app.include_router(contact.router)
app.include_router(match_data_router.router)
@app.on_event("startup")
async def startup():
    scheduler.start()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
