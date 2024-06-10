from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, Text, DateTime, Integer, Sequence
from sqlalchemy.orm import declarative_base

Base = declarative_base()

#SQLAlchemy model
class Livestream_links(Base):
    __tablename__ = "livestream_links"
    model_config = ConfigDict(from_attributes=True)
    id = Column(Integer, primary_key=True)
    time = Column(String(50))
    match = Column(String(50))
    url = Column(String(200))
    date = Column(DateTime)

#modelin duhet me check!!

#Pydantic Model
class Livestream_link_Model(BaseModel):
    time: str
    match: str
    url: str
    date: str


