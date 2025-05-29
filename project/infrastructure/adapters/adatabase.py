import contextvars
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
)

from project.settings import Settings

asession_storage: contextvars.ContextVar[AsyncSession | None] = contextvars.ContextVar("current_session", default=None)


@lru_cache
def aengine_factory() -> AsyncEngine:
    return create_async_engine(
        str(Settings().SQLALCHEMY_DATABASE_DSN),
        pool_pre_ping=Settings().DATABASE_PRE_PING,
    )


@lru_cache
def async_sessionmaker_factory():
    return async_sessionmaker(aengine_factory(), autoflush=False, expire_on_commit=False)


@asynccontextmanager
async def asession():
    """
    This function ensures that a session is reused if one already exists,
    otherwise it creates a new session for the asynchronous operation.
    The session is properly cleaned up after use, avoiding resource leaks.
    """
    current_session = asession_storage.get()

    if current_session:
        yield current_session
    else:
        async_session = async_sessionmaker_factory()
        async with async_session() as session:
            token = asession_storage.set(session)
            try:
                yield session
            finally:
                asession_storage.reset(token)


@asynccontextmanager
async def atransaction():
    """
    During the call, a transaction is created,
    and with an nested call inside another transaction,
    SavePoint is created.
    """
    current_session = asession_storage.get()

    if current_session:
        if current_session.in_transaction():
            async with current_session.begin_nested():
                yield current_session
        else:
            async with current_session.begin():
                yield current_session
    else:
        async with asession() as session:
            yield session


@asynccontextmanager
async def current_atransaction():
    """
    Creates a new transaction if it does not open or returns the current transaction.
    """
    current_session = asession_storage.get()

    if current_session:
        if current_session.in_transaction():
            yield current_session
        else:
            async with current_session.begin():
                yield current_session
    else:
        async with asession() as session:
            yield session
