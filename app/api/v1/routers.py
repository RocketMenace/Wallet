from fastapi import APIRouter, status, HTTPException
from uuid import UUID
from dishka.integrations.fastapi import inject, FromDishka
from app.config.logger import get_logger
from app.exceptions import WalletNotFoundError
from app.schemas.response import ApiResponseSchema
from app.schemas.wallet import WalletResponseSchema, WalletCreateSchema
from app.use_cases import CreateWalletUseCase
from app.use_cases import GetWalletUseCase
from fastapi.exceptions import RequestValidationError


logger = get_logger(__name__)
router = APIRouter(prefix="/v1/wallets", tags=["Wallets v1"])


@router.post(
    path="",
    summary="Create new wallet",
    description="""
    Create a new wallet with an optional initial balance.

    This endpoint allows users to create a new wallet in the system. The wallet will be assigned a unique UUID and timestamp for creation and last update.

    **Parameters:**
    - `balance` (optional): Initial balance for the wallet. Defaults to 0.00 if not provided. Must be a non-negative decimal value.

    **Response Body:**
    - "id": Unique identifier for the created wallet
    - "balance": Current wallet balance
    - "created_at": Timestamp when the wallet was created
    - "updated_at": Timestamp when the wallet was last updated
    """,
    response_model=ApiResponseSchema[WalletResponseSchema],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Wallet created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "balance": "100.50",
                            "created_at": "2025-10-22T10:30:00Z",
                            "updated_at": "2025-10-22T10:30:00Z",
                        },
                        "meta": {"path": "/v1/wallets", "method": "POST"},
                        "errors": [],
                    },
                },
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {"path": "/v1/wallets", "method": "POST"},
                        "errors": [
                            {
                                "field": "balance",
                                "message": "ensure this value is greater than or equal to 0",
                                "input": -100,
                            },
                        ],
                    },
                },
            },
        },
    },
)
@inject
async def create(
    schema: WalletCreateSchema,
    use_case: FromDishka["CreateWalletUseCase"],
):
    logger.info("Create wallet request received")
    try:
        data = await use_case.execute(schema=schema)
        return ApiResponseSchema(data=data, meta={}, errors=[])
    except RequestValidationError as e:
        logger.error("Failed to create wallet", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=e.errors(),
        )


@router.get(
    path="/{wallet_id}",
    summary="Retrieve wallet data",
    description="""
            Retrieve wallet information by wallet ID.

            This endpoint allows users to fetch detailed information about a specific wallet using its unique identifier.

            **Parameters:**
            - `wallet_id` (path parameter): The unique UUID identifier of the wallet to retrieve

            **Response Body:**
            - "id": Unique identifier for the wallet
            - "balance": Current wallet balance
            - "created_at": Timestamp when the wallet was created
            - "updated_at": Timestamp when the wallet was last updated
            """,
    response_model=ApiResponseSchema[WalletResponseSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Wallet retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "balance": "100.50",
                            "created_at": "2025-10-22T10:30:00Z",
                            "updated_at": "2025-10-22T15:45:30Z",
                        },
                        "meta": {
                            "path": "/v1/wallets/550e8400-e29b-41d4-a716-446655440000",
                            "method": "GET",
                        },
                        "errors": [],
                    },
                },
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Wallet not found",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {
                            "path": "/v1/wallets/550e8400-e29b-41d4-a716-446655440000",
                            "method": "GET",
                        },
                        "errors": [
                            {
                                "message": "Wallet with ID 550e8400-e29b-41d4-a716-446655440000 not found",
                            },
                        ],
                    },
                },
            },
        },
    },
)
@inject
async def get_wallet(wallet_id: UUID, use_case: FromDishka["GetWalletUseCase"]):
    logger.info("Get wallet request received")
    try:
        data = await use_case.execute(wallet_id=wallet_id)
        return ApiResponseSchema(data=data, meta={}, errors=[])
    except WalletNotFoundError as e:
        logger.error("Failed to retrieve wallet data", error=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
