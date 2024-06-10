from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import secrets
from sqlalchemy.orm import Session
from app.models.user import UserDB
from pydantic import ValidationError
from app.database import get_db

# Secret key for token signing (keep this secret)
SECRET_KEY = "ede2ac3b38a9bdc5d90eb58c9e379f34cd18c8ffafa3b254c3879f15b8039f05"

# Algorithm to use for token signing
ALGORITHM = "HS256"

# Token expiration time (e.g., 15 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 180

# Function to create an access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Create a CryptContext instance for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash a password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



def generate_verification_token():
    return secrets.token_urlsafe(32)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(db: Session = Depends(get_db), token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        user = db.query(UserDB).filter(UserDB.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# ...

# OAuth2PasswordBearer is a FastAPI security scheme to get the access token from a request

