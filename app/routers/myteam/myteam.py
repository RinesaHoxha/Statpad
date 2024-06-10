from fastapi import APIRouter, Query, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_, asc, desc, func

from app.models.highlights import HighlightsDB
from app.models.last_match import LastMatches
from app.models.lineup import Lineup, LineupModel
from app.models.form import Form, FormDB
from app.models.form import Form, FormDB
from app.models.stadiums import Stadiums
from app.models.stadiums_info import Stadiumsinfo
from app.models.standing import LeagueTable
from app.models.team import Team,Team_model
from app.models.team_next_clash import NextMatches
from app.models.user import UserDB
from app.routers.Predictions.Predictions import matches, predict_winner
from app.routers.user.security import get_current_user
from app.database import SessionLocal, get_db
from app.models.news import News

router = APIRouter(
    prefix='/myteam',
    tags=['myteam']
)
templates=Jinja2Templates(directory='templates')

@router.get('/favoriteteam')
def get_favorite_team(request: Request):
    # Access the auth token directly from the cookies
    auth_token = request.cookies.get("Authorization")

    if not auth_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Fetch user data by making a request to an authentication endpoint
    user_data = fetch_user_data(auth_token)

    if user_data is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    favorite_team = user_data.get("favorite_team")

    db = SessionLocal()

    # Query Lineup with the filter based on the favorite_team
    lineup = db.query(Lineup).filter(Lineup.team.ilike(f"%{favorite_team}%")).all()
    forms = db.query(FormDB).filter(FormDB.team_name.ilike(f"%{favorite_team}%")).all()
    hg = db.query(HighlightsDB).filter(HighlightsDB.match_name.ilike(f"%{favorite_team}%")).order_by(desc(func.to_date(HighlightsDB.date, 'DD-MM-YYYY')))
    last_match = db.query(LastMatches).filter(
        or_(LastMatches.h_name.ilike(f"%{favorite_team}%"), LastMatches.a_name.ilike(f"%{favorite_team}%"))
    ).order_by(desc(LastMatches.date)).all()

    league_table = db.query(LeagueTable).filter(LeagueTable.club.ilike(f"%{favorite_team}%")).all()
    stadiums = db.query(Stadiumsinfo).filter(Stadiumsinfo.team.ilike(f"%{favorite_team}%")).all()
    team = db.query(Team).filter(Team.team.ilike(f"%{favorite_team}%")).all()
    next_match= db.query(NextMatches).filter(
        or_(NextMatches.h_name.ilike(f"%{favorite_team}%"), NextMatches.a_name.ilike(f"%{favorite_team}%"))
    ).order_by(asc(NextMatches.date)).all()
    news = db.query(News).all()


    # Close the database session
    db.close()


    return templates.TemplateResponse('myteam.html', {
        'request': request,
        'lineup': lineup,
        'team': team,
        'hg':hg,
        'forms': forms,
        'league_table': league_table,
        'next_match': next_match,
        'last_match': last_match,
        'stadiums': stadiums,
        'news': news,
        'favorite_team': favorite_team
    })


# Function to fetch user data by making a request to an authentication endpoint
def fetch_user_data(token):
    import requests

    headers = {"Authorization": token}
    response = requests.get("http://localhost:8080/api/user-profile", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None