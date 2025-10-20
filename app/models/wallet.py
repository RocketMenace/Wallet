from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models.base import BaseModel
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from uuid import UUID, uuid4
from sqlalchemy import Float, Enum as SQLEnum
from app.models.enums import OperationType


class Wallet(BaseModel):
    __tablename__ = "wallets"
    balance: Mapped[float] = mapped_column(Float, default=0.0)

    # === RELATIONSHIPS ===
    transactions: Mapped["Transaction"] = relationship(
        back_populates="wallet",
        passive_deletes=True,
        foreign_keys="[Transaction.wallet_id]",
    )


class Transaction(BaseModel):
    __tablename__ = "transactions"
    id: Mapped[UUID] = mapped_column(SQLUUID, primary_key=True, default=uuid4)
    wallet_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True))
    kind: Mapped[OperationType] = mapped_column(SQLEnum(OperationType))

    # === RELATIONSHIPS ===
    wallet: Mapped["Wallet"] = relationship(
        back_populates="transactions", foreign_keys=[wallet_id]
    )
