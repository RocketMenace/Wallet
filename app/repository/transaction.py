from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.base import BaseRepository
from app.models.wallet import Transaction


class TransactionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(session=session, model=Transaction)
