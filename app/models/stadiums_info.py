from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Stadiumsinfo(Base):
    __tablename__ = "stadiumsinfo"
    id=Column(Integer,primary_key=True)
    stadium_name=Column(String)
    image=Column(String)
    city=Column(String)
    address=Column(String)
    construction_date=Column(String)
    capacity=Column(String)
    size=Column(String)
    grass_type=Column(String)
    phone=Column(String)
    fax=Column(String)
    team=Column(String)

class StadiumsinfoModel(BaseModel):
    stadium_name:str
    image:str
    city:str
    address:str
    construction_date:str
    capacity:str
    size:str
    grass_type:str
    phone:str
    fax:str
    team:str
