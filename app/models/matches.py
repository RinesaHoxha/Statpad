import datetime
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LiveSoccerScores(Base):
    __tablename__ = 'live_soccer_scores'

    id = Column(Integer, primary_key=True)
    league_img = Column(String)
    league = Column(String)
    round = Column(String)
    home_team = Column(String)
    home_team_img = Column(String)
    away_team = Column(String)
    away_team_img = Column(String)
    score = Column(String)
    match_status = Column(String)
    match_date = Column(DateTime)
    date_scraped = Column(DateTime)

class TomorrowSoccerScores(Base):
    __tablename__ = 'tomorrow_soccer_scores'

    id = Column(Integer, primary_key=True)
    league_img = Column(String)
    league = Column(String)
    round = Column(String)
    home_team = Column(String)
    home_team_img = Column(String)
    away_team = Column(String)
    away_team_img = Column(String)
    score = Column(String)
    match_status=Column(String)
    match_date = Column(DateTime)
    date_scraped = Column(DateTime)

class MatchesPydantic(BaseModel):
    league_img : str
    league:str
    round:str
    home_team :str
    home_team_img :str
    away_team :str
    away_team_img :str
    score : str
    match_status : str
    match_date : str
    date_scraped : str


class MatchesPydantic(BaseModel):
    league_img: str
    league:str
    round:str
    home_team :str
    home_team_img :str
    away_team :str
    away_team_img :str
    score : str
    match_status: str
    match_date : str
    date_scraped : str


