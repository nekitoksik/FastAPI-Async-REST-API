from fastapi import HTTPException

from app.models.user import User
from app.schemas.user import SUser

from app.database import async_session_maker
from sqlalchemy import insert, select

class UserService():
    model = User

    @classmethod
    async def get_user_by_id(cls, user_id: int) -> SUser:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=user_id)
            result = await session.execute(query)

            user_data = result.fetchone()
            if not user_data:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            return SUser(user_data)
    
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