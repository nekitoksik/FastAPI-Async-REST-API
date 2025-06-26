from fastapi import APIRouter, Depends, HTTPException
from app.schemas.transaction import WebhookRequest
from app.services.transaction.process_transaction import TransactionService

from app.models.user import User
from app.services.user.service import UserService
from app.services.user.dependencies import get_current_user
from app.schemas.transaction import STransaction

router = APIRouter(
    prefix="/transactions",
    tags=["Транзакции"],
)

@router.get('', response_model=list[STransaction])
async def get_all_transactions(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=404, detail="Вы не являетесь админом!")
    

    transactions = await TransactionService.get_all_transactions()
    return [STransaction.model_validate(tr) for tr in transactions]



@router.post("/process-transaction")
async def process_transaction(data: WebhookRequest):
    return await TransactionService.process_transaction(data)


@router.post("/get-test-signature")
async def get_test_signature(data: WebhookRequest):
    return {"signature": f"{TransactionService.generate_signature(data.model_dump())}"}