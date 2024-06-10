from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class CoachesDB(Base):
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True, index=True)
    coach_name = Column(String)
    club_name = Column(String)
    coach_logo = Column(String)
    team_logo = Column(String)
    nationality_flag = Column(String)

class Coaches(BaseModel):
    coach_name: str
    club_name: str
    coach_logo: str
    team_logo: str
    nationality_flag: str
