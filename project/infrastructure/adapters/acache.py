import contextvars
from contextlib import asynccontextmanager
from functools import cache
from typing import Any, AsyncGenerator

import redis
from redis.asyncio.client import Pipeline

from project.settings import Settings

redis_async_transactions: contextvars.ContextVar[Pipeline | None] = contextvars.ContextVar(
    "current_transaction",
    default=None,
)


@cache
def RedisAsyncClient() -> redis.asyncio.Redis:  # noqa: N802
    return redis.asyncio.Redis(
        host=Settings().REDIS_HOST,
        port=int(Settings().REDIS_PORT),
        db=int(Settings().REDIS_DB),
    )


@asynccontextmanager
async def local_redis_async_transaction() -> AsyncGenerator[Pipeline, Any]:
    """
    Creates an isolated Redis transaction using a new pipeline.
    Executes the transaction on context exit.
    """
    client = RedisAsyncClient()

    async with client.pipeline() as pipe:
        yield pipe
        await pipe.execute()


@asynccontextmanager
async def context_redis_async_transaction() -> AsyncGenerator[Pipeline, Any]:
    """
    Reuses an existing transaction pipeline if available in the current context.
    Otherwise, creates a new one, stores it in the context, and ensures execution.
    """
    current_transaction = redis_async_transactions.get()

    if current_transaction:
        yield current_transaction

    else:
        client = RedisAsyncClient()

        async with client.pipeline() as pipe:
            token = redis_async_transactions.set(pipe)

            try:
                yield pipe
                await pipe.execute()

            finally:
                redis_async_transactions.reset(token)
