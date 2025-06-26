from fastapi import APIRouter, HTTPException, Response, Depends, status
from pydantic import BaseModel

from app.schemas.account import SAccountCreate
from app.services.account.services import AccountService
router = APIRouter(
    prefix="/accounts",
    tags=["Счета"],
)

@router.post("/create-account/{user_id}")
async def create_account(data: SAccountCreate):
    return await AccountService.create_new_account(data)