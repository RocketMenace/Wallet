from datetime import datetime
from enum import Enum

from .base import BasePydanticModel
from uuid import UUID
from pydantic import Field
from decimal import Decimal


class OperationType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class TransactionBaseSchema(BasePydanticModel):
    wallet_id: UUID = Field(..., description="Wallet ID")
    amount: Decimal = Field(..., description="Transaction amount", ge=0)
    kind: OperationType = Field(..., description="Operation type")


class TransactionCreateSchema(TransactionBaseSchema):
    pass


class TransactionResponseSchema(TransactionBaseSchema):
    id: UUID = Field(..., description="Transaction ID")
    created_at: datetime = Field(..., description="Transaction creating date")
    updated_at: datetime = Field(..., description="Wallet balance update date")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
                    "amount": "100.50",
                    "kind": "deposit",
                    "created_at": "2025-10-22T10:30:00Z",
                    "updated_at": "2025-10-22T10:30:00Z",
                },
                {
                    "id": "123e4567-e89b-12d3-a456-426614174001",
                    "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
                    "amount": "25.75",
                    "kind": "withdraw",
                    "created_at": "2025-10-22T11:15:30Z",
                    "updated_at": "2025-10-22T11:15:30Z",
                },
            ],
        },
    }
