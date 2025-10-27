from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.base import BaseRepository
from app.models.wallet import Wallet
from app.schemas.wallet import WalletResponseSchema


class WalletRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            model=Wallet,
        )

    async def get_by_uuid(self, uuid: UUID) -> WalletResponseSchema | None:
        query = select(self.model).where(self.model.id == uuid).with_for_update()
        result = (await self.session.execute(query)).scalar_one_or_none()
        return result
