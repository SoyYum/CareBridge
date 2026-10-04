from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(value):
    return pwd.hash(value)

def verify_password(value, hashed):
    return pwd.verify(value, hashed)

def create_token(user_id):
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expiry}, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def current_user(token: str = Depends(oauth), db: Session = Depends(get_db)):
    error = HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        uid = int(payload["sub"])
    except (JWTError, ValueError, KeyError, TypeError):
        raise error
    user = db.get(User, uid)
    if not user:
        raise error
    return user
