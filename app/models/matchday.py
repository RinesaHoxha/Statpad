from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Matchday(Base):
    __tablename__ = "matchday"
    model_config = ConfigDict(from_attributes=True)
    id = Column(Integer, primary_key=True)
    matchweek = Column(String)
    league = Column(String)
    h_team = Column(String)
    a_team = Column(String)
    h_image = Column(String)
    a_image = Column(String)
    time = Column(String)
    date = Column(String)


# Pydantic Model
class Matchday_model(BaseModel):
    matchweek : str
    league: str
    h_name: str
    a_name: str
    h_image: str
    a_image: str
    time: str
    date: str
