from pydantic import BaseModel, EmailStr

class SUserBase(BaseModel):
    id: int
    email: EmailStr
    full_name: str

class SUserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class SUserLogin(BaseModel):
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
    email: EmailStr | None = None
    password: str | None = None
    full_name: str | None = None
    is_admin: bool | None = None