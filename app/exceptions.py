from typing import Optional

from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, status, Response, Request, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.response import ApiResponseSchema
from app.schemas.exceptions import CoreServiceExceptionSchema
from uuid import UUID


class CoreServiceException(Exception):
    def __init__(self, message: str, detail: str):
        self.message = message
        self.detail = detail

    def get_schema(self) -> CoreServiceExceptionSchema:
        return CoreServiceExceptionSchema(message=self.message, detail=self.detail)


class WalletNotFoundError(CoreServiceException):
    def __init__(self, wallet_id: UUID, message: Optional[str] = None):
        self.wallet_id = wallet_id
        self.message = message or f"Wallet with ID {wallet_id} not found"
        super().__init__(message=self.message, detail=f"Wallet ID: {wallet_id}")

    def get_schema(self) -> CoreServiceExceptionSchema:
        return CoreServiceExceptionSchema(message=self.message, detail=self.detail)


class NotEnoughCredits(CoreServiceException):
    def __init__(self, wallet_id: UUID, message: Optional[str] = None):
        self.wallet_id = wallet_id
        self.message = message or f"Wallet ID {wallet_id} not enough credits"
        super().__init__(message=self.message, detail=f"Wallet ID: {wallet_id}")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(WalletNotFoundError)
    def wallet_not_found_handler(
        request: Request,
        exc: WalletNotFoundError,
    ) -> Response:
        error_detail = {
            "message": exc.message,
            "field": "wallet_id",
            "detail": exc.detail,
        }

        response_schema: ApiResponseSchema = ApiResponseSchema(
            errors=[error_detail],
            data={},
            meta={"path": str(request.url.path), "method": request.method},
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response_schema.model_dump(),
        )

    @app.exception_handler(NotEnoughCredits)
    def not_enough_credits_handler(request: Request, exc: NotEnoughCredits) -> Response:
        error_detail = {
            "message": exc.message,
            "detail": exc.detail,
        }
        response_schema: ApiResponseSchema = ApiResponseSchema(
            errors=[error_detail],
            data={},
            meta={"path": str(request.url.path), "method": request.method},
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response_schema.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> Response:
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"][1:])
            errors.append(
                {
                    "field": field,
                    "message": error["msg"],
                    "input": error.get("input"),
                },
            )

        response_schema: ApiResponseSchema = ApiResponseSchema(
            errors=errors,
            data={},
            meta={
                "path": str(request.url.path),
                "method": request.method,
            },
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=response_schema.model_dump(),
        )

    @app.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException) -> Response:
        error_detail = {
            "message": str(exc.detail),
        }

        response_schema: ApiResponseSchema = ApiResponseSchema(
            errors=[error_detail],
            data={},
            meta={"path": str(request.url.path), "method": request.method},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response_schema.model_dump(),
        )
