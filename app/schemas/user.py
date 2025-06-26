from pydantic import BaseModel, EmailStr

class SUserBase(BaseModel):
    email: EmailStr
    full_name: str 

class SUserCreate(SUserBase):
    password: str

class SUserLogin(BaseModel):
    email: EmailStr
    password: str

class SUser(SUserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

