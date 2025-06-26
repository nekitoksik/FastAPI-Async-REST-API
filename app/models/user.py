from app.database import Base
from sqlalchemy import Boolean, Integer, String
from app.models.account import Account
from app.models.payment import Payment 
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(300), nullable=False)
    full_name: Mapped[str] = mapped_column(String(300), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    accounts = relationship("Account", back_populates="user")
    payments = relationship("Payment", back_populates="user")

