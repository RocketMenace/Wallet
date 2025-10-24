from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models.base import BaseModel
from uuid import UUID
from sqlalchemy import (
    Enum as SQLEnum,
    NUMERIC,
    ForeignKey,
    CheckConstraint,
    Index,
)
from app.models.enums import OperationType
from decimal import Decimal


class Wallet(BaseModel):
    __tablename__ = "wallets"
    balance: Mapped[Decimal] = mapped_column(NUMERIC(19, 2), default=Decimal("0.00"))

    # === RELATIONSHIPS ===
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="wallet",
        cascade="all, delete-orphan",
    )

    # === TABLE ARGS ===
    __table_args__ = (CheckConstraint("balance >= 0", name="non_negative_balance"),)


class Transaction(BaseModel):
    __tablename__ = "transactions"

    wallet_id: Mapped[UUID] = mapped_column(
        ForeignKey("wallets.id", ondelete="CASCADE"),
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(NUMERIC(19, 2))
    kind: Mapped[OperationType] = mapped_column(SQLEnum(OperationType))

    # === RELATIONSHIPS ===
    wallet: Mapped["Wallet"] = relationship(back_populates="transactions")
    # === TABLE ARGS ===
    __table_args__ = (
        CheckConstraint("amount > 0", name="positive_amount"),
        Index("idx_transaction_wallet_created", "wallet_id", "created_at"),
    )
