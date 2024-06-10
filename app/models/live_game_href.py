import datetime
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Live_game_href(Base):
    __tablename__ = 'live_game_href'
    id = Column(Integer, primary_key=True)
    href_link = Column(String)
    team_1 = Column(String)
    team_2 = Column(String)


class Live_game_href_model(BaseModel):
    href_link: str
    team_1: str
    team_2: str
