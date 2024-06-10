from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Stadiums(Base):
    __tablename__ = "stadiums"
    model_config = ConfigDict(from_attributes=True)
    id = Column(Integer, primary_key=True)
    img = Column(String)
    name = Column(String)
    year = Column(String)
    capacity = Column(String)
    team = Column(String)


# Pydantic Model
class Stadiums_model(BaseModel):
    img: str
    name: str
    year: str
    capacity: str
    team: str
