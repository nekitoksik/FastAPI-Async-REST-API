from fastapi import Depends, Request, HTTPException
from jose import jwt, JWTError
from datetime import datetime, timezone

from app.config import settings
from app.services.user.service import UserService


def get_token(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=404, detail="Токен не найден")
    
    return token

async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )

    except:
        raise HTTPException(status_code=404, detail="Неправильный токен")
    
    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=404, detail="Токен не валиден")
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user = await UserService.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

        
    return user