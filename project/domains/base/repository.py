from contextlib import contextmanager
from typing import TypeVar, Any, Generator

from sqlalchemy import delete, orm

from project.infrastructure.adapters.database import Session, Transaction, CurrentTransaction
from project.domains.base.models import Base

T = TypeVar("T", bound=Base)


class BaseRepository[T]:
    """
    Separates infrastructure from ORM.
    """

    _model: type[T]

    @classmethod
    @contextmanager
    def session(cls) -> Generator[orm.Session, Any, None]:
        with Session() as session:
            yield session

    @classmethod
    @contextmanager
    def transaction(cls) -> Generator[orm.Session, Any, None]:
        with Transaction() as session:
            yield session

    @classmethod
    @contextmanager
    def current_transaction(cls) -> Generator[orm.Session, Any, None]:
        with CurrentTransaction() as session:
            yield session


class Repository[T](BaseRepository):
    """
    Separates infrastructure from ORM.
    """

    @classmethod
    def new(cls, **kwargs: Any) -> T:
        return cls._model(**kwargs)

    @classmethod
    def create(cls, **kwargs: Any) -> T:
        instance = cls.new(**kwargs)
        cls.save(instance)
        return instance

    @classmethod
    def save(cls, instance: T) -> None:
        with cls.transaction() as session:
            session.add(instance)

    @classmethod
    def get_or_none(cls, pk: Any) -> T | None:
        with cls.session() as session:
            return session.get(cls._model, pk)

    @classmethod
    def update_fields(cls, instance: T, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(instance, key, value)

    @classmethod
    def update_and_save(cls, instance: T, **kwargs: Any) -> None:
        with cls.transaction():
            for key, value in kwargs.items():
                setattr(instance, key, value)

    @classmethod
    def delete_by_id(cls, id: Any) -> None:
        with cls.transaction() as session:
            session.execute(delete(cls._model).where(cls._model.id == id))
