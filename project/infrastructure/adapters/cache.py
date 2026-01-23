import contextvars
from contextlib import contextmanager
from functools import cache
from typing import Any, Generator

import redis
from redis.client import Pipeline

from project.settings import Settings

redis_transactions: contextvars.ContextVar[Pipeline | None] = contextvars.ContextVar(
    "current_transaction",
    default=None,
)


@cache
def RedisClient() -> redis.Redis:  # noqa: N802
    return redis.Redis(
        host=Settings().REDIS_HOST,
        port=Settings().REDIS_PORT,
        db=Settings().REDIS_DB,
    )


@contextmanager
def isolated_redis_transaction() -> Generator[Pipeline, Any, None]:
    """
    Creates an isolated Redis transaction using a new pipeline.
    Executes the transaction on context exit.
    """
    client = RedisClient()

    with client.pipeline() as pipe:
        yield pipe
        pipe.execute()


@contextmanager
def redis_transaction() -> Generator[Pipeline, Any, None]:
    """
    Reuses an existing transaction pipeline if available in the current context.
    Otherwise, creates a new one, stores it in the context, and ensures execution.
    """
    current_transaction = redis_transactions.get()

    if current_transaction:
        yield current_transaction

    else:
        client = RedisClient()

        with client.pipeline() as pipe:
            token = redis_transactions.set(pipe)

            try:
                yield pipe
                pipe.execute()

            finally:
                redis_transactions.reset(token)
