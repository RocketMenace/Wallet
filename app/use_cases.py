from app.services.wallet import WalletService
from app.schemas.wallet import WalletCreateSchema, WalletResponseSchema
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
