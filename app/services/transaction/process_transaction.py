from fastapi import HTTPException, status

from jose import jwt
import hashlib
from app.config import settings
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User
from app.database import async_session_maker
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from app.schemas.transaction import WebhookRequest

class TransactionService:
    model = Transaction

    @classmethod
    async def get_all_transactions(cls):
        async with async_session_maker() as session:
            transactions = await session.execute(select(Transaction))
            
            return transactions.scalars().all()

    @classmethod
    def generate_signature(cls, transaction_data: dict) -> str:
        signature = (
            f"{transaction_data['account_id']}"
            f"{transaction_data['amount']}"
            f"{transaction_data['transaction_id']}"
            f"{transaction_data['user_id']}"
            f"{settings.SECRET_KEY}"
        )

        return hashlib.sha256(signature.encode()).hexdigest()
    
    @classmethod
    def verify_signature(cls, recieved_signature: str, transaction_data: dict):
        generated_signature = cls.generate_signature(transaction_data)

        if not generated_signature == recieved_signature:
            return False
        
        return True


    @classmethod
    async def process_transaction(cls, webhook_data: WebhookRequest):
        async with async_session_maker() as session:

            if not cls.verify_signature(webhook_data.signature, webhook_data.model_dump()):
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Сигнатура не релевантна")
            
            query = select(Transaction).where(Transaction.transaction_id == webhook_data.transaction_id)
            existing_transaction = await session.execute(query)
            existing_transaction = existing_transaction.scalar()

            if existing_transaction:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Транзакция уже обработана")

            user = await session.execute(select(User).where(User.id == webhook_data.user_id))
            user = user.scalar()

            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
            
            account = await session.execute(
                select(Account).where(
                    Account.id == webhook_data.account_id,
                    Account.user_id == webhook_data.user_id
                )
            )
            account = account.scalar()

            if not account:
                #не было уточнений с каким id создавать новый счет, но так как, возможен вариант, когда у пользователя нет счета с id = 2
                #но такой счет будет у другого пользователя, то будет невозможно создать новый счет с тем id, который передавался в webhook,
                #я решил создавать новый счет со свободным id и возвращать уже этот id
                account = Account(
                    user_id=webhook_data.user_id,
                    balance=0
                )
                session.add(account)
            print(account)
            account.balance += webhook_data.amount

            await session.commit()
            await session.refresh(account)#обновляю для получения id

            
            transaction = Transaction(
                user_id=webhook_data.user_id,
                transaction_id=webhook_data.transaction_id,
                account_id=account.id,
                amount=webhook_data.amount
            )

            session.add(transaction)
            await session.commit()

            return transaction


            
            