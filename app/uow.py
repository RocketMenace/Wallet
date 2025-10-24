from typing import Self, Protocol, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.transaction import TransactionRepository
from app.repository.wallet import WalletRepository


class UnitOfWorkProtocol(Protocol):
    wallets: WalletRepository
    transactions: TransactionRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._wallets: Optional[WalletRepository] = None
        self._transactions: Optional[TransactionRepository] = None

    @property
    def wallets(self) -> WalletRepository:
        if self._wallets is None:
            self._wallets = WalletRepository(self.session)
        return self._wallets

    @property
    def transactions(self) -> TransactionRepository:
        if self._transactions is None:
            self._transactions = TransactionRepository(self.session)
        return self._transactions

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
