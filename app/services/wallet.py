from app.exceptions import WalletNotFoundError
from app.schemas.wallet import WalletResponseSchema, WalletCreateSchema
from app.uow import UnitOfWorkProtocol
from uuid import UUID


class WalletService:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    async def get_wallet(self, wallet_id: UUID) -> WalletResponseSchema:
        async with self.uow as uow:
            wallet = await uow.wallets.get_by_uuid(uuid=wallet_id)
            if not wallet:
                raise WalletNotFoundError(
                    wallet_id=wallet_id,
                    message=f"Wallet with ID {wallet_id} not found",
                )
            return wallet

    async def create_wallet(self, schema: WalletCreateSchema) -> WalletResponseSchema:
        async with self.uow as uow:
            wallet = await uow.wallets.create(schema=schema)
            await uow.commit()
            return wallet
