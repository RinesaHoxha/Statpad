import datetime
from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    title=Column(String(500))
    url = Column(String(500))
    image_url=Column(String(500))
    context=Column(String(500))
    dateposted = Column(String(200))
    date_scraped = Column(DateTime)

class NewsPydantic(BaseModel):
    id: int
    title:str
    url: str
    image_url:str
    context:str
    dateposted: str
    date_scraped: datetime.datetime


