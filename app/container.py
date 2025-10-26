from dishka import make_async_container
from .dependencies import (
    SessionProvider,
    ServiceProvider,
    UnitOfWorkProvider,
    UseCaseProvider,
    OperationFactoryProvider,
)

container = make_async_container(
    SessionProvider(),
    UnitOfWorkProvider(),
    OperationFactoryProvider(),
    ServiceProvider(),
    UseCaseProvider(),
)
