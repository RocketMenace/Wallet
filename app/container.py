from dishka import make_async_container
from .dependencies import (
    SessionProvider,
    ServiceProvider,
    UnitOfWorkProvider,
    UseCaseProvider,
)

container = make_async_container(
    SessionProvider(),
    UnitOfWorkProvider(),
    ServiceProvider(),
    UseCaseProvider(),
)
