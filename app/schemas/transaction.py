from pydantic import BaseModel


class STransactionCreate(BaseModel):
    transaction_id: str
    user_id: int
    account_id: int
    amount: float

class STransaction(STransactionCreate):
    id: int
    
    class Config:
        from_attributes = True

class WebhookRequest(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: float
    signature: str

    class Config:
        from_attributes = True
    