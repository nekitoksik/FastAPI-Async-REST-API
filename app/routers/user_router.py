from fastapi import APIRouter, HTTPException, Response

from app.services.user.service import UserService
from app.schemas.user import SUser, SUserCreate, SUserLogin
from app.services.user.auth import get_password_hash, create_access_token, verify_user

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get("")
async def get_users() -> list[SUser]:
    result = await UserService.get_all_users()

    return result


@router.get("/{user_id}")
async def get_user_by_id(user_id: int) -> SUser:
    result = await UserService.get_user_by_id(user_id)

    return result

@router.post("/register")
async def register_user(user_data: SUserCreate):
    existing_user = await UserService.get_one_user(email=user_data.email)

    if existing_user:
        raise HTTPException(status_code=404, detail="Такой пользователь уже существует")
    
    hashed_password = get_password_hash(user_data.password)
    user_data.password = hashed_password
    await UserService.add_new_user(**user_data)



@router.post("/login")
async def login_user(response: Response, user_data: SUserLogin):
    user = await verify_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    access_token = create_access_token({"sub": str(user.id)})    
    response.set_cookie("access_token", access_token, httponly=True)
    return access_token



@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")