from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel


Base = declarative_base()

class HighlightsDB(Base):
    __tablename__ = "highlights"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    competition = Column(String)
    match_name = Column(String, unique=True, index=True)
    video_link = Column(String)

class Highlights(BaseModel):
    date: str
    competition: str
    match_name: str
    video_link: str





