import asyncio
from typing import AsyncIterator, AsyncGenerator
from app.models.wallet import Wallet

import httpx
import pytest
import pytest_asyncio
from dishka import make_async_container, Provider, Scope, provide
from dishka.integrations.fastapi import setup_dishka
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import (
    UnitOfWorkProvider,
    OperationFactoryProvider,
    ServiceProvider,
    UseCaseProvider,
)
from app.main import create_application
from tests.test_database import create_test_engine, create_test_session_factory


class TestSessionProvider(Provider):
    scope = Scope.REQUEST

    def __init__(self):
        super().__init__()
        self.engine = create_test_engine()
        self.session_factory = create_test_session_factory(self.engine)

    @provide
    async def provide_test_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.engine.begin() as conn:
            await conn.run_sync(Wallet.metadata.create_all)

        async with self.session_factory() as session:
            yield session
            await session.commit()

        # await self.engine.dispose()


@pytest_asyncio.fixture
async def container():
    container = make_async_container(
        TestSessionProvider(),
        UnitOfWorkProvider(),
        OperationFactoryProvider(),
        ServiceProvider(),
        UseCaseProvider(),
    )
    yield container
    await container.close()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def get_async_client(container) -> AsyncIterator[httpx.AsyncClient]:
    app = create_application()
    setup_dishka(container=container, app=app)
    client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://localhost:8000",
    )
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def connection(container):
    return await container.get(TestSessionProvider)


@pytest_asyncio.fixture(scope="function")
async def create_test_wallet_id(get_async_client):
    client = get_async_client
    response = await client.post("/api/v1/wallets", json={"balance": "1000.00"})
    return response.json()["data"]["id"]
