from fastapi import APIRouter, HTTPException, Response, Depends, status
from pydantic import BaseModel

from app.models.user import User

from app.services.user.service import UserService
from app.services.user.dependencies import get_current_user
from app.services.user.auth import get_password_hash, verify_password, create_access_token, verify_user
from app.database import async_session_maker

from app.schemas.user import SUser, SUserCreate, SUserLogin, SUserBase, SUserRegister, SUserUpdate
from app.schemas.account import SAccount
from app.schemas.transaction import STransaction


router = APIRouter(
    prefix="/admin",
    tags=["Админ роутеры"],
)

@router.get("/get-users")
async def get_users(current_user: User = Depends(get_current_user)) -> list[SUser]:
    '''Получение всех пользователей'''
    if not current_user.is_admin:
        raise HTTPException(status_code=404, detail="Вы не являетесь админом!")
    
    result = await UserService.get_all_users()

    return result

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    '''Получение данных о себе'''
    return SUserBase.model_validate(current_user)


@router.post("/register")
async def register_user(user_data: SUserRegister):
    '''Регистрация пользователя'''
    existing_user = await UserService.get_one_user(email=user_data.email)

    if existing_user:
        raise HTTPException(status_code=404, detail="Такой пользователь уже существует")
    
    hashed_password = get_password_hash(user_data.password)
    
    user_dict = user_data.model_dump()
    user_dict["password"] = hashed_password
    user_dict["is_admin"] = True
    await UserService.add_new_user(**user_dict)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login")
async def login_user(response: Response, user_data: SUserLogin) -> TokenResponse:
    '''Авторизация пользователя'''
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


#admin routes
@router.post("/create-user")
async def create_user(user_data: SUserCreate, current_user: User = Depends(get_current_user)):
    '''Создание пользователя'''
    if not current_user.is_admin:
        raise HTTPException(status_code=404, detail="Вы не являетесь админом!")
    
    if await UserService.get_one_user(email=user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    db_user_data = user_data.model_copy()
    db_user_data.password = get_password_hash(user_data.password)

    await UserService.add_new_user(**db_user_data.model_dump())
    db_user = await UserService.get_one_user(email=user_data.email)

    return User(
        id=db_user.id,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        is_admin=user_data.is_admin
    )


@router.delete("/delete-user/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    '''Удаление пользователя'''
    if not current_user.is_admin:
        raise HTTPException(status_code=404, detail="Вы не являетесь админом!")
    
    if not await UserService.get_one_user(id=user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не найден"
        )

    return await UserService.delete_user(user_id)

@router.patch("/update-user/{user_id}")
async def update_user(user_id: int, update_data: SUserUpdate, current_user: User = Depends(get_current_user)):
    '''Обновление пользователя'''
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Недостаточно прав для обновления пользователя"
        )

    user_to_update = await UserService.get_user_by_id(user_id)
    if not user_to_update:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    db_data = update_data.model_copy()

    db_data.password = get_password_hash(update_data.password)
    db_data = db_data.model_dump()
    updated_user = await UserService.update_user(user_id, db_data)

    return User(
        id=updated_user.id,
        email=updated_user.email,
        password=update_data.password,
        full_name=updated_user.full_name,
        is_admin=updated_user.is_admin
    )


@router.get("/{user_id}")
async def get_user_by_id(user_id: int) -> SUser:
    '''Получение данных о пользователе по id'''
    result = await UserService.get_user_by_id(user_id)

    return result


@router.get("/get-user-accounts/{user_id}", response_model=list[SAccount])
async def get_user_accounts(user_id: int, current_user: User = Depends(get_current_user)):
    '''Получение балансов пользователя'''
    if not current_user.is_admin:
        raise HTTPException(status_code=404, detail="Вы не являетесь админом!")
    
    user = await UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден!")

    accounts = await UserService.get_user_accounts(user_id)
    return [SAccount.model_validate(account) for account in accounts]