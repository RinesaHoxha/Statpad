from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, validator
from datetime import datetime
from sqlalchemy.orm import relationship
from typing import Optional

Base = declarative_base()

class LoginUser(BaseModel):
    username: str
    password: str

class SignupUser(BaseModel):
    full_name: str
    username: str
    email: str
    password: str
    favorite_team: str

class FullNameUpdate(BaseModel):
    full_name: str

class UsernameUpdate(BaseModel):
    username: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UserDB(Base):  
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    email  = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False)  # New field for email verification
    verification_token = Column(String, unique=True, index=True)
    favorite_team = Column(String, nullable=False)
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")

class UserInDB(SignupUser):
    id: int
    created_at: datetime

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("UserDB", back_populates="posts")

class PostCreate(BaseModel):
    content: str

class PostInDB(PostCreate):
    id: int
    user_id: int
    created_at: datetime

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("UserDB", back_populates="comments")


class CommentCreate(BaseModel):
    content: str

class CommentInDB(CommentCreate):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
