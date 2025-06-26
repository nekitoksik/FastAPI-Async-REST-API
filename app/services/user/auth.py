from fastapi import HTTPException

from passlib.hash import pbkdf2_sha256 as sha256
from datetime import datetime, timedelta, timezone
from pydantic import EmailStr

from jose import jwt

from app.services.user.service import UserService
from app.models.user import User
from app.config import settings

def get_password_hash(password: str) -> str:
    return sha256.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return sha256.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=10)
    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, settings.ALGORITHM
        )
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Ошибка создания токена{e}")

    return encoded_jwt

async def verify_user(email: EmailStr, password: str) -> User:
    existing_user = await UserService.get_one_user(email=email)

    if not existing_user and not verify_password(password, existing_user.password):
        raise HTTPException(status_code=404, detail="Пароли не совпадают")
    
    return existing_user