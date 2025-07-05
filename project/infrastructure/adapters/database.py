import contextvars
from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session as ORMSession, scoped_session

from project.domains.base.models import public_schema
from project.settings import Settings

session_storage: contextvars.ContextVar[ORMSession | None] = contextvars.ContextVar("current_session", default=None)


@lru_cache
def engine_factory() -> Engine:
    return create_engine(
        str(Settings().SQLALCHEMY_DATABASE_DSN),
        pool_pre_ping=Settings().DATABASE_PRE_PING,
    )


@lru_cache
def scoped_session_factory() -> scoped_session:
    engine = engine_factory()
    return scoped_session(
        sessionmaker(
            engine,
            autoflush=False,
            expire_on_commit=False,
            autobegin=True,
        )
    )


@contextmanager
def Session() -> Generator[ORMSession, Any, None]:
    """
    This function ensures that a session is reused if one already exists,
    otherwise it creates a new session.
    The session is properly cleaned up after use, avoiding resource leaks.
    """
    current_session = session_storage.get()

    if current_session:
        yield current_session
    else:
        ScopedSession = scoped_session_factory()
        with ScopedSession() as session:
            token = session_storage.set(session)
            try:
                yield session
            finally:
                session_storage.reset(token)


@contextmanager
def Transaction() -> Generator[ORMSession, Any, None]:
    """
    During the call, a transaction is created,
    and with an nested call inside another transaction,
    SavePoint is created.
    """
    current_session = session_storage.get()

    if current_session:
        if current_session.in_transaction():
            with current_session.begin_nested():
                yield current_session
        else:
            with current_session.begin():
                yield current_session
    else:
        with Session() as current_session:
            if current_session.in_transaction():
                with current_session.begin_nested():
                    yield current_session
            else:
                with current_session.begin():
                    yield current_session


@contextmanager
def CurrentTransaction() -> Generator[ORMSession, Any, None]:
    """
    With a repeated opening of the transaction, a new transaction is not created,
    but an early open transaction is used.
    """
    current_session = session_storage.get()

    if current_session:
        if current_session.in_transaction():
            yield current_session
        else:
            with current_session.begin():
                yield current_session
    else:
        with Session() as current_session:
            if current_session.in_transaction():
                yield current_session
            else:
                with current_session.begin():
                    yield current_session


def init_database():
    engine = engine_factory()
    public_schema.create_all(bind=engine)
