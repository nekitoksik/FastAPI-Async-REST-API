from fastapi import HTTPException

from app.models.account import Account
from app.models.user import User
from app.schemas.account import SAccount, SAccountCreate
from app.database import async_session_maker
from sqlalchemy import insert, select, delete, update

class AccountService:
    model = Account

    @classmethod
    async def create_new_account(cls, data: SAccountCreate):
        async with async_session_maker() as session:
            user = await session.get(User, data.user_id)

            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            new_account = Account(
                user_id=data.user_id,
                balance=data.balance
            )
            
            session.add(new_account)
            await session.commit()

            return new_account