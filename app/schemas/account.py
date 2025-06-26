from pydantic import BaseModel

class SAccount(BaseModel):
    id: int
    user_id: int
    balance: float

    class Config:
        from_attributes = True

class SAccountCreate(BaseModel):
    user_id: int
    balance: float = 0

