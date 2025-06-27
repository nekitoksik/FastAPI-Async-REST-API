from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.user_router import router as user_router
from app.routers.admin_router import router as admin_router
from app.routers.transaction_router import router as transaction_router
from app.routers.account_router import router as account_router


app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # В продакшене укажите конкретные домены
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(transaction_router)
app.include_router(account_router)
