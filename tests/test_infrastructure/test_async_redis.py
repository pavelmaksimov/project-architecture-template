import pytest

from project.infrastructure.adapters.acache import context_redis_async_transaction, local_redis_async_transaction


@pytest.mark.asyncio
async def test_async_local_transaction(async_redis):
    async with local_redis_async_transaction() as tr:
        tr.set("foo", "bar")
        tr.set("bar", "baz")

        assert await async_redis.get("foo") == None
        assert await async_redis.get("bar") == None

    assert await async_redis.get("foo") == b"bar"
    assert await async_redis.get("bar") == b"baz"


@pytest.mark.asyncio
async def test_async_context_transaction(async_redis):
    async with context_redis_async_transaction() as tr:
        tr.set("foo", "bar")

        assert await async_redis.get("foo") == None
        assert await async_redis.get("bar") == None

        async with context_redis_async_transaction() as ltr:
            assert tr == ltr

            ltr.set("bar", "baz")

            assert await async_redis.get("foo") == None
            assert await async_redis.get("bar") == None

        assert await async_redis.get("bar") == None
        assert await async_redis.get("foo") == None

    assert await async_redis.get("foo") == b"bar"
    assert await async_redis.get("bar") == b"baz"


@pytest.mark.asyncio
async def test_async_context_with_local_transaction(async_redis):
    assert await async_redis.get("foo") == None
    assert await async_redis.get("bar") == None

    async with context_redis_async_transaction() as tr:
        tr.set("foo", "bar")

        assert await async_redis.get("foo") == None
        assert await async_redis.get("bar") == None

        async with local_redis_async_transaction() as ltr:
            assert tr != ltr

            ltr.set("bar", "baz")

            assert await async_redis.get("foo") == None
            assert await async_redis.get("bar") == None

        assert await async_redis.get("bar") == b"baz"
        assert await async_redis.get("foo") == None

    assert await async_redis.get("foo") == b"bar"
