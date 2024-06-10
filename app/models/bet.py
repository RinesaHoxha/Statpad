import datetime
from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Bets(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True)
    liga = Column(String(200))
    date = Column(String(50))
    team1 = Column(String(100))
    team2 = Column(String(100))
    odds_1 = Column(Float)
    odds_x = Column(Float)
    odds_2 = Column(Float)
    date_scraped = Column(DateTime)


class BetModel(BaseModel):
    id: int
    liga: str
    date: str
    team1: str
    team2: str
    odds_1: float
    odds_x: float
    odds_2: float
    date_scraped: datetime.datetime
