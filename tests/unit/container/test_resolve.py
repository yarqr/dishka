import pytest

from dishka import (
    Provider,
    Scope,
    make_async_container,
    make_container,
    provide,
)
from ..sample_providers import (
    A_VALUE,
    ClassA,
    async_func_a,
    async_gen_a,
    async_iter_a,
    sync_func_a,
    sync_gen_a,
    sync_iter_a,
    value_factory,
)


@pytest.mark.parametrize(
    ("factory", "closed"),
    [
        (ClassA, False),
        (sync_func_a, False),
        (sync_iter_a, True),
        (sync_gen_a, True),
    ],
)
def test_sync(factory, closed):
    class MyProvider(Provider):
        a = provide(factory, scope=Scope.APP)

        @provide(scope=Scope.APP)
        def get_int(self) -> int:
            return 100

    container = make_container(MyProvider())
    a = container.get(ClassA)
    assert a
    assert a.dep == 100
    container.close()
    assert a.closed == closed


@pytest.mark.parametrize(
    ("factory", "closed"),
    [
        (ClassA, False),
        (sync_func_a, False),
        (sync_iter_a, True),
        (sync_gen_a, True),
        (async_func_a, False),
        (async_iter_a, True),
        (async_gen_a, True),
    ],
)
@pytest.mark.asyncio
async def test_async(factory, closed):
    class MyProvider(Provider):
        a = provide(factory, scope=Scope.APP)

        @provide(scope=Scope.APP)
        def get_int(self) -> int:
            return 100

    container = make_async_container(MyProvider())
    a = await container.get(ClassA)
    assert a
    assert a.dep == 100
    await container.close()
    assert a.closed == closed


def test_value():
    class MyProvider(Provider):
        factory = value_factory

    container = make_container(MyProvider())
    assert container.get(ClassA) is A_VALUE


@pytest.mark.asyncio
async def test_value_async():
    class MyProvider(Provider):
        factory = value_factory

    container = make_async_container(MyProvider())
    assert await container.get(ClassA) is A_VALUE


class OtherClass:
    def method(self) -> ClassA:
        return A_VALUE

    @classmethod
    def classmethod(cls) -> ClassA:
        return A_VALUE

    @staticmethod
    def staticmethod() -> ClassA:
        return A_VALUE


@pytest.mark.parametrize("method", [
    OtherClass().method,
    OtherClass().classmethod,
    OtherClass().staticmethod,
])
def test_external_method(method):
    provider = Provider(scope=Scope.APP)
    provider.provide(method)

    container = make_container(provider)
    assert container.get(ClassA) is A_VALUE
