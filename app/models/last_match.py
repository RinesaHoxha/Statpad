import datetime
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LastMatches(Base):
    __tablename__ = 'last_matches'


    id = Column(Integer, primary_key=True)
    team_name = Column(String)
    status = Column(String)
    result = Column(String)
    league = Column(String)
    h_name = Column(String)
    a_name = Column(String)
    h_image = Column(String)
    a_image = Column(String)
    date = Column(String)


class LastMatchesPydantic(BaseModel):
    team_name : str
    status : str
    result : str
    league : str
    h_name : str
    a_name : str
    h_image : str
    a_image : str
    date : str