from pydantic import BaseModel

class Account(BaseModel):
    id: int
    user_id: int
    balance: float

class AccountCreate(BaseModel):
    user_id: int
    balance: float = 0

