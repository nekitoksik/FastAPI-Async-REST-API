from app.database import Base
from sqlalchemy import Integer, String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    balance: Mapped[float] = mapped_column(Float, nullable=False)

    user = relationship("User", back_populates="accounts")
    payments = relationship("Payment", back_populates="account")
