from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import PickleType
from sqlalchemy.ext.mutable import MutableList

Base = declarative_base()


class Team(Base):
    __tablename__ = "team"
    model_config = ConfigDict(from_attributes=True)
    id = Column(Integer, primary_key=True)
    job_title = Column(String)
    number = Column(String)
    image = Column(String)
    name = Column(String)
    team_performance = Column(MutableList.as_mutable(PickleType), default=[])
    team_info = Column(MutableList.as_mutable(PickleType), default=[])
    team = Column(String)



# Pydantic Model
class Team_model(BaseModel):
    job_title: str
    name: str
    number: str
    image: str
    team_performance: list = []
    team_info: list = []
    team: str

