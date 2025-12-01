import pytest

from project.infrastructure.adapters.acache import redis_atransaction, isolated_redis_atransaction


@pytest.mark.asyncio
async def test_async_local_transaction(async_redis):
    async with isolated_redis_atransaction() as tr:
        tr.set("foo", "bar")
        tr.set("bar", "baz")

        assert await async_redis.get("foo") == None
        assert await async_redis.get("bar") == None

    assert await async_redis.get("foo") == b"bar"
    assert await async_redis.get("bar") == b"baz"


@pytest.mark.asyncio
async def test_async_context_transaction(async_redis):
    async with redis_atransaction() as tr:
        tr.set("foo", "bar")

        assert await async_redis.get("foo") == None
        assert await async_redis.get("bar") == None

        async with redis_atransaction() as ltr:
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

    async with redis_atransaction() as tr:
        tr.set("foo", "bar")

        assert await async_redis.get("foo") == None
        assert await async_redis.get("bar") == None

        async with isolated_redis_atransaction() as ltr:
            assert tr != ltr

            ltr.set("bar", "baz")

            assert await async_redis.get("foo") == None
            assert await async_redis.get("bar") == None

        assert await async_redis.get("bar") == b"baz"
        assert await async_redis.get("foo") == None

    assert await async_redis.get("foo") == b"bar"


@pytest.mark.asyncio
async def test_delete(async_redis):
    await async_redis.set("foo", "bar")
    assert await async_redis.get("foo") == b"bar"

    async with isolated_redis_atransaction() as tr:
        await tr.delete("foo")

    assert await async_redis.get("foo") == None
