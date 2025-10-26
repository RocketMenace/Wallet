from dishka import Scope, provide, Provider
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import database
from app.services import WalletService
from app.services.transaction import (
    OperationFactoryProtocol,
    TransactionService,
    OperationFactory,
)
from app.uow import UnitOfWork, UnitOfWorkProtocol
from app.use_cases import GetWalletUseCase, CreateWalletUseCase, UpdateBalanceUseCase


class SessionProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with database.get_session() as session:
            yield session


class UnitOfWorkProvider(Provider):
    scope = Scope.REQUEST

    @provide(provides=UnitOfWorkProtocol)
    async def provide_unit_of_work(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session=session)


class OperationFactoryProvider(Provider):
    scope = Scope.REQUEST

    @provide(provides=OperationFactoryProtocol)
    async def provide_operation_factory(self) -> OperationFactory:
        return OperationFactory()


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_wallet_service(self, uow: UnitOfWorkProtocol) -> WalletService:
        return WalletService(uow=uow)

    @provide
    async def provide_transactions_service(
        self,
        operation_factory: OperationFactoryProtocol,
        uow: UnitOfWorkProtocol,
    ) -> TransactionService:
        return TransactionService(operation_factory=operation_factory, uow=uow)


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_create_wallet_use_case(
        self,
        wallets_service: WalletService,
    ) -> CreateWalletUseCase:
        return CreateWalletUseCase(wallets_service=wallets_service)

    @provide
    async def provide_get_wallet_use_case(
        self,
        wallet_service: WalletService,
    ) -> GetWalletUseCase:
        return GetWalletUseCase(wallets_service=wallet_service)

    @provide
    async def provide_update_balance_use_case(
        self,
        transactions_service: TransactionService,
    ) -> UpdateBalanceUseCase:
        return UpdateBalanceUseCase(transactions_service=transactions_service)
