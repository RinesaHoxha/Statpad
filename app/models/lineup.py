import datetime
from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Lineup(Base):
    __tablename__ = "lineup"

    id = Column(Integer, primary_key=True)
    team = Column(String(200))
    number = Column(String(50))
    name = Column(String(200))



class LineupModel(BaseModel):
    team: str
    number: str
    name:str
