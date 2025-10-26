from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


def create_test_engine():
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=None,
    )


def create_test_session_factory(engine):
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
