from pydantic import BaseModel


class PaymentCreate(BaseModel):
    transaction_id: int
    user_id: int
    account_id: int
    amount: float
    signature: str

class Payment(PaymentCreate):
    id: int

    class Config:
        from_attributes = True