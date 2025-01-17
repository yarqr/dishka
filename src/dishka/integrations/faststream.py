from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, ParamSpec, TypeVar

from faststream import BaseMiddleware, FastStream, context
from faststream.types import DecodedMessage

from dishka.async_container import AsyncContainer
from dishka.integrations.base import Depends, wrap_injection

__all__ = (
    "Depends",
    "inject",
    "setup_dishka",
)

P = ParamSpec("P")
T = TypeVar("T")


def inject(func: Callable[P, T]) -> Callable[P, T]:
    return wrap_injection(
        func=func,
        container_getter=lambda *_: context.get_local("dishka"),
        is_async=True,
        remove_depends=True,
    )


class DishkaMiddleware(BaseMiddleware):
    def __init__(self, container: AsyncContainer) -> None:
        self.container = container

    def __call__(self, msg: Any | None = None) -> "DishkaMiddleware":
        self.msg = msg
        return self

    @asynccontextmanager
    async def consume_scope(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncIterator[DecodedMessage]:
        async with self.container() as request_container:
            with context.scope("dishka", request_container):
                async with super().consume_scope(*args, **kwargs) as result:
                    yield result


def setup_dishka(
    container: AsyncContainer,
    app: FastStream,
    *,
    finalize_container: bool = True,
) -> None:
    assert app.broker, "You can't patch FastStream application without broker"  # noqa: S101

    if finalize_container:
        app.after_shutdown(container.close)

    app.broker.middlewares = (
        *app.broker.middlewares,
        DishkaMiddleware(container),
    )
