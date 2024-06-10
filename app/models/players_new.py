from pydantic import BaseModel
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Players(Base):
    __tablename__ = "players_new"

    id = Column(Integer, primary_key=True)
    rank = Column(Integer)
    player_image_url = Column(String(500))
    player_name = Column(String(500))
    club_name = Column(String(500))
    goals = Column(Integer)
    nationality = Column(String(200))
    age = Column(Integer)
    assists = Column(Integer)
    league_name = Column(String(200))

class PlayerPydantic(BaseModel):
    id: int
    rank: int
    player_image_url: str
    player_name: str
    club_name: str
    goals: int
    nationality: str
    age: int
    assists: int
    league_name: str
