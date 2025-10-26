from app.exceptions import WalletNotFoundError
from app.uow import UnitOfWorkProtocol
from uuid import UUID
from app.schemas.transaction import TransactionCreateSchema, TransactionResponseSchema
from typing import Protocol, Type
from app.models.enums import OperationType
from app.exceptions import NotEnoughCredits


class OperationProtocol(Protocol):
    async def execute(
        self,
        wallet_id: UUID,
        payload: TransactionCreateSchema,
    ) -> TransactionResponseSchema: ...


class OperationFactoryProtocol(Protocol):
    def make(
        self,
        operation_type: OperationType,
        uow: UnitOfWorkProtocol,
    ) -> OperationProtocol: ...


class DepositOperation:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    async def execute(
        self,
        wallet_id: UUID,
        payload: TransactionCreateSchema,
    ) -> TransactionResponseSchema:
        async with self.uow as uow:
            wallet = await uow.wallets.get_raw_model_by_uuid(uuid=wallet_id)
            if not wallet:
                raise WalletNotFoundError(
                    wallet_id=wallet_id,
                    message=f"Wallet with ID {wallet_id} not found",
                )

            wallet.balance += payload.amount

            transaction_data = payload.model_copy(update={"wallet_id": wallet_id})
            transaction = await uow.transactions.create(schema=transaction_data)
            await uow.commit()
            return TransactionResponseSchema.model_validate(transaction)


class WithDrawOperation:
    def __init__(self, uow: UnitOfWorkProtocol):
        self.uow = uow

    async def execute(
        self,
        wallet_id: UUID,
        payload: TransactionCreateSchema,
    ) -> TransactionResponseSchema:
        async with self.uow as uow:
            wallet = await uow.wallets.get_raw_model_by_uuid(uuid=wallet_id)
            if not wallet:
                raise WalletNotFoundError(wallet_id=wallet_id)

            if wallet.balance < payload.amount:
                raise NotEnoughCredits(wallet_id=wallet_id)

            wallet.balance -= payload.amount

            transaction_data = payload.model_copy(update={"wallet_id": wallet_id})
            transaction = await uow.transactions.create(schema=transaction_data)
            await uow.commit()
            return TransactionResponseSchema.model_validate(transaction)


class OperationFactory:
    @staticmethod
    def make(
        operation_type: OperationType,
        uow: UnitOfWorkProtocol,
    ) -> DepositOperation | WithDrawOperation:
        operations_mapper: dict[
            OperationType,
            Type[DepositOperation | WithDrawOperation],
        ] = {
            OperationType.DEPOSIT: DepositOperation,
            OperationType.WITHDRAW: WithDrawOperation,
        }
        return operations_mapper[operation_type](uow=uow)


class TransactionService:
    def __init__(
        self,
        operation_factory: OperationFactoryProtocol,
        uow: UnitOfWorkProtocol,
    ):
        self.operation_factory = operation_factory
        self.uow = uow

    async def handle_operation(
        self,
        wallet_id: UUID,
        payload: TransactionCreateSchema,
    ) -> TransactionResponseSchema:
        operation = self.operation_factory.make(
            operation_type=payload.kind,
            uow=self.uow,
        )
        return await operation.execute(wallet_id=wallet_id, payload=payload)
