from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LeagueTable(Base):
    __tablename__ = "league_tables"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(String)
    imageurl=Column(String)
    club = Column(String(500))
    plays=Column(String)
    wins=Column(Integer)
    draws=Column(Integer)
    losses=Column(Integer)
    goalsscored=Column(Integer)
    goalsconceded=Column(Integer)
    goaldifference=Column(Integer)
    points = Column(Integer)

# Pydantic model for input data
class LeagueTableCreate(BaseModel):
    position: str
    imageurl: str
    club: str
    plays: int
    wins: int
    draws: int
    losses: int
    goalsscored: int
    goalsconceded: int
    goaldifference: int
    points: int