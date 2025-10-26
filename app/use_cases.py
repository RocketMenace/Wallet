from app.services.wallet import WalletService
from app.services.transaction import TransactionService
from app.schemas.wallet import WalletCreateSchema, WalletResponseSchema
from app.schemas.transaction import TransactionCreateSchema, TransactionResponseSchema
from uuid import UUID


class CreateWalletUseCase:
    def __init__(self, wallets_service: WalletService):
        self.wallets_service = wallets_service

    async def execute(self, schema: WalletCreateSchema) -> WalletResponseSchema:
        return await self.wallets_service.create_wallet(schema=schema)


class GetWalletUseCase:
    def __init__(self, wallets_service: WalletService):
        self.wallets_service = wallets_service

    async def execute(self, wallet_id: UUID) -> WalletResponseSchema:
        return await self.wallets_service.get_wallet(wallet_id=wallet_id)


class UpdateBalanceUseCase:
    def __init__(self, transactions_service: TransactionService):
        self.transactions_service = transactions_service

    async def execute(
        self,
        wallet_id: UUID,
        payload: TransactionCreateSchema,
    ) -> TransactionResponseSchema:
        return await self.transactions_service.handle_operation(
            wallet_id=wallet_id,
            payload=payload,
        )
