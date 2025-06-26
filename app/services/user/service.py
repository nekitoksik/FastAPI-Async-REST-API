from fastapi import HTTPException

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.user import SUser

from app.database import async_session_maker
from sqlalchemy import insert, select, delete, update

class UserService:
    model = User

    @classmethod
    async def get_user_by_id(cls, user_id: int) -> SUser:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=user_id)
            result = await session.execute(query)

            user_data = result.scalar_one_or_none()
            if not user_data:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            return SUser.model_validate(user_data)
    
    @classmethod
    async def get_one_user(cls, **data) -> SUser:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**data)
            result = await session.execute(query)

            return result.scalar_one_or_none()
        
    @classmethod
    async def get_all_users(cls) -> list[SUser]:
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)

            return result.scalars().all()
        

    @classmethod
    async def add_new_user(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()

            return
        
    @classmethod
    async def delete_user(cls, user_id: int):
        async with async_session_maker() as session:
            user = await session.get(User, user_id)

            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            delete_query = delete(cls.model).where(cls.model.id == user_id)
            await session.execute(delete_query)
            await session.commit()

            return
    
    @classmethod
    async def update_user(cls, user_id: int, update_data: dict):
        async with async_session_maker() as session:

            query = (
                update(cls.model)
                .where(cls.model.id == user_id)
                .values(**update_data)
                .returning(cls.model)
            )
            result = await session.execute(query)
            await session.commit()

            update_user = result.scalar_one()
            return update_user
    
    @classmethod
    async def get_user_accounts(cls, user_id: int) -> list[Account]:
        async with async_session_maker() as session:
            query = select(Account).where(Account.user_id==user_id)
            user_accounts = await session.execute(query)

            return user_accounts.scalars().all()
    
    @classmethod
    async def get_user_transactions(cls, user_id: int) -> list[Transaction]:
        async with async_session_maker() as session:
            query = select(Transaction).where(Transaction.user_id==user_id)
            user_transactions = await session.execute(query)

            return user_transactions.scalars().all()