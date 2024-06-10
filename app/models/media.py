from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class MediaDB(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    link = Column(String)

class Media(BaseModel):
    text: str
    link: str
