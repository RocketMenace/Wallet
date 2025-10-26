from typing import Protocol, TypeVar, Any
from uuid import UUID

from app.models.base import BaseModel
from pydantic import BaseModel as Schema

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert


ModelType = TypeVar("ModelType", bound=BaseModel)
ResponseSchema = TypeVar("ResponseSchema", bound=Schema)
UpdateSchema = TypeVar("UpdateSchema", bound=Schema)


class BaseRepositoryProtocol(Protocol):
    async def create(self, schema: Schema) -> Any: ...
    async def get_list(self, offset: int, limit: int) -> list[Any]: ...
    async def get_by_uuid(self, uuid: UUID) -> Any: ...
    async def update(self, uuid: UUID, schema: Any) -> Any: ...
    async def delete(self, uuid: UUID) -> None: ...


class BaseRepository:
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def create(self, schema: Schema) -> Any:
        query = insert(self.model).values(**schema.model_dump()).returning(self.model)
        result = (await self.session.execute(query)).scalar_one()
        return result

    async def get_by_uuid(self, uuid: UUID) -> Any | None:
        query = select(self.model).where(self.model.id == uuid)
        result = (await self.session.execute(query)).scalar_one_or_none()
        return result
