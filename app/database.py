from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.matches import Base as MatchesBase
from app.models.user import Base as UserBase
from app.models.news import Base as NewsBase
from app.models.livestream_links import Base as LSBase
from app.models.highlights import Base as HLBase
from app.models.players import Base as PlayersBase
from app.models.standing import Base as StandingsBase
from app.models.bet import Base as BetBase
from app.models.coaches import Base as CoachesBase
from app.models.media import Base as MediaBase
from app.models.stadiums import Base as StadiumBase
from app.models.matchday import Base as MatchdayBase
from app.models.form import Base as FormBase
from app.models.team import Base as TeamBase
from app.models.lineup import Base as LineupBase
from app.models.last_match import Base as LastMatchesBase
from app.models.team_next_clash import Base as NextMatchesBase
from app.models.live_game_href import Base as href_Base
from app.models.stadiums_info import Stadiumsinfo
from app.models.players_new import Base as PlayersNewBase
from fastapi import FastAPI


from decouple import config

# Initialize FastAPI app
app = FastAPI()

# Configure the database connection
DATABASE_URL = config("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Create tables if they don't exist

TeamBase.metadata.create_all(bind=engine)
NewsBase.metadata.create_all(bind=engine)
MatchesBase.metadata.create_all(bind=engine)
UserBase.metadata.create_all(bind=engine)
LSBase.metadata.create_all(bind=engine)
StandingsBase.metadata.create_all(bind=engine)
PlayersBase.metadata.create_all(bind=engine)
HLBase.metadata.create_all(bind=engine)
BetBase.metadata.create_all(bind=engine)
CoachesBase.metadata.create_all(bind=engine)
MediaBase.metadata.create_all(bind=engine)
StadiumBase.metadata.create_all(bind=engine)
MatchdayBase.metadata.create_all(bind=engine)
FormBase.metadata.create_all(bind=engine)
LineupBase.metadata.create_all(bind=engine)
LastMatchesBase.metadata.create_all(bind=engine)
NextMatchesBase.metadata.create_all(bind=engine)
href_Base.metadata.create_all(bind=engine)
Stadiumsinfo.metadata.create_all(bind=engine)
PlayersNewBase.metadata.create_all(bind=engine)



# Create a session for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



