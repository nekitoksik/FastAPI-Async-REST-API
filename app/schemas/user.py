from pydantic import BaseModel, EmailStr
from typing import Optional

class SUserBase(BaseModel):
    id: int
    email: EmailStr
    full_name: str

class SUserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class SUserLogin(BaseModel):
    email: EmailStr
    password: str

class SUserCreate(SUserRegister):
    is_admin: bool

class SUser(SUserBase):
    is_admin: bool

    class Config:
        from_attributes = True

class SUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_admin: Optional[bool] = None