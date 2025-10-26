from fastapi import APIRouter, status, HTTPException
from uuid import UUID
from dishka.integrations.fastapi import inject, FromDishka
from app.config.logger import get_logger
from app.exceptions import WalletNotFoundError, NotEnoughCredits
from app.schemas.response import ApiResponseSchema
from app.schemas.wallet import WalletResponseSchema, WalletCreateSchema
from app.use_cases import CreateWalletUseCase, GetWalletUseCase, UpdateBalanceUseCase
from fastapi.exceptions import RequestValidationError
from app.schemas.transaction import TransactionResponseSchema, TransactionCreateSchema


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


@router.post(
    path="/{wallet_id}/operation",
    summary="Process financial operation",
    description="""
    Process a financial operation (deposit or withdrawal) for a specific wallet.

    This endpoint allows users to perform financial operations on an existing wallet. The operation can be either a deposit (adding money to the wallet) or a withdrawal (removing money from the wallet).

    **Parameters:**
    - `wallet_id` (path parameter): The unique UUID identifier of the wallet to perform the operation on
    - `amount` (request body): The amount to deposit or withdraw. Must be a non-negative decimal value
    - `kind` (request body): The type of operation - either "deposit" or "withdraw"

    **Response Body:**
    - "id": Unique identifier for the created transaction
    - "wallet_id": The wallet ID this operation was performed on
    - "amount": The transaction amount
    - "kind": The operation type (deposit/withdraw)
    - "created_at": Timestamp when the transaction was created
    - "updated_at": Timestamp when the wallet balance was last updated
    """,
    response_model=ApiResponseSchema[TransactionResponseSchema],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Operation processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "wallet_id": "550e8400-e29b-41d4-a716-446655440000",
                            "amount": "100.50",
                            "kind": "deposit",
                            "created_at": "2025-10-22T10:30:00Z",
                            "updated_at": "2025-10-22T10:30:00Z",
                        },
                        "meta": {
                            "path": "/v1/wallets/550e8400-e29b-41d4-a716-446655440000/operation",
                            "method": "POST",
                        },
                        "errors": [],
                    },
                },
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Insufficient funds for withdrawal",
            "content": {
                "application/json": {
                    "example": {
                        "data": {},
                        "meta": {
                            "path": "/v1/wallets/550e8400-e29b-41d4-a716-446655440000/operation",
                            "method": "POST",
                        },
                        "errors": [
                            {
                                "message": "Wallet ID 550e8400-e29b-41d4-a716-446655440000 not enough credits",
                                "detail": "Wallet ID: 550e8400-e29b-41d4-a716-446655440000",
                            },
                        ],
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
                            "path": "/v1/wallets/550e8400-e29b-41d4-a716-446655440000/operation",
                            "method": "POST",
                        },
                        "errors": [
                            {
                                "message": "Wallet with ID 550e8400-e29b-41d4-a716-446655440000 not found",
                                "field": "wallet_id",
                                "detail": "Wallet ID: 550e8400-e29b-41d4-a716-446655440000",
                            },
                        ],
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
                        "meta": {
                            "path": "/v1/wallets/550e8400-e29b-41d4-a716-446655440000/operation",
                            "method": "POST",
                        },
                        "errors": [
                            {
                                "field": "amount",
                                "message": "ensure this value is greater than or equal to 0",
                                "input": -50.0,
                            },
                        ],
                    },
                },
            },
        },
    },
)
@inject
async def handle_operation(
    wallet_id: UUID,
    payload: TransactionCreateSchema,
    use_case: FromDishka["UpdateBalanceUseCase"],
):
    logger.info("Handle operation request received")
    try:
        data = await use_case.execute(wallet_id=wallet_id, payload=payload)
        return ApiResponseSchema(data=data, meta={}, errors=[])
    except WalletNotFoundError as e:
        logger.error("Failed to retrieve wallet data", error=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except NotEnoughCredits as e:
        logger.error("Failed to process operation", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
