from datetime import datetime

from app.schemas.base import BasePydanticModel
from pydantic import Field
from decimal import Decimal
from uuid import UUID


class WalletBaseSchema(BasePydanticModel):
    balance: Decimal = Field(..., description="Wallet balance")


class WalletCreateSchema(BasePydanticModel):
    balance: Decimal | None = Field(
        default=Decimal("0.00"),
        description="Wallet initial balance",
        ge=0,
    )


class WalletResponseSchema(WalletBaseSchema):
    id: UUID = Field(..., description="Wallet ID")
    created_at: datetime = Field(..., description="Wallet creating date")
    updated_at: datetime = Field(..., description="Wallet balance update date")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "balance": "1000.50",
                    "created_at": "2025-10-22T10:30:00Z",
                    "updated_at": "2025-10-22T15:45:30Z",
                },
            ],
        },
    }
