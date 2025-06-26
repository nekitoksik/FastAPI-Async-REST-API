from fastapi import APIRouter, HTTPException, Response, Depends, status
from pydantic import BaseModel

from app.models.user import User

from app.services.user.service import UserService
from app.services.user.dependencies import get_current_user
from app.services.user.auth import get_password_hash, create_access_token, verify_user

from app.schemas.user import SUser, SUserCreate, SUserLogin, SUserBase, SUserRegister, SUserUpdate
from app.schemas.account import SAccount
from app.schemas.transaction import STransaction


router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    '''Получение данных о себе'''
    return SUserBase.model_validate(current_user)

@router.get("/get-my-accounts", response_model=list[SAccount])
async def get_user_accounts(current_user: User = Depends(get_current_user)):
    '''Получение балансов пользователя'''
    accounts = await UserService.get_user_accounts(current_user.id)
    return [SAccount.model_validate(account) for account in accounts]


@router.get("/get-my-transactions", response_model=list[STransaction])
async def get_user_transactions(current_user: User = Depends(get_current_user)):
    '''Получение транзакций пользователя'''
    transactions = await UserService.get_user_transactions(current_user.id)
    return [STransaction.model_validate(transaction) for transaction in transactions]


@router.post("/register")
async def register_user(user_data: SUserRegister):
    '''Регистрация пользователя'''
    existing_user = await UserService.get_one_user(email=user_data.email)

    if existing_user:
        raise HTTPException(status_code=404, detail="Такой пользователь уже существует")
    
    hashed_password = get_password_hash(user_data.password)
    
    user_dict = user_data.model_dump()
    user_dict["password"] = hashed_password
    await UserService.add_new_user(**user_dict)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login")
async def login_user(response: Response, user_data: SUserLogin):
    user = await verify_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    access_token = create_access_token({"sub": str(user.id)})    
    response.set_cookie("access_token", access_token, httponly=True)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout_user(response: Response):
    '''Выход из аккаунта(Удаление токена из cookie)'''
    response.delete_cookie("access_token")
