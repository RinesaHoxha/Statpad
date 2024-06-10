from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

# Model for scraped form data
class FormDB(Base):
    __tablename__ = "form_data"

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String)
    competition_logo = Column(String)
    date = Column(String)
    home_scores = Column(String)
    away_scores = Column(String)
    enemy_logo = Column(String)
    h_or_a = Column(String)

# Pydantic model for scraped form data
class Form(BaseModel):
    team_name: str
    competition_logo: str
    date: str
    home_scores: str
    away_scores: str
    enemy_logo: str
    h_or_a: str
