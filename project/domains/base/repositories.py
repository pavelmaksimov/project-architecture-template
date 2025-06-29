from contextlib import contextmanager
from typing import TypeVar, Any, Generator

from sqlalchemy import select, delete, orm

from project.domains.base.exceptions import NotFoundError, throw
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
    def get_session(cls) -> Generator[orm.Session, Any, None]:
        with Session() as session:  # di: skip
            yield session

    @classmethod
    @contextmanager
    def get_transaction(cls) -> Generator[orm.Session, Any, None]:
        with Transaction() as session:  # di: skip
            yield session

    @classmethod
    @contextmanager
    def get_current_transaction(cls) -> Generator[orm.Session, Any, None]:
        with CurrentTransaction() as session:  # di: skip
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
        with cls.get_transaction() as session:
            session.add(instance)

    @classmethod
    def get_or_none(cls, pk: Any) -> T | None:
        with cls.get_session() as session:
            return session.get(cls._model, pk)

    def get(self, pk: Any) -> T:
        return self.get_or_none(pk) or throw(NotFoundError, f"{self._model}.pk", pk)

    def all(self):
        with self.get_session() as session:
            return session.scalars(select(self._model)).all()

    @classmethod
    def update_fields(cls, instance: T, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(instance, key, value)

    @classmethod
    def update_and_save(cls, instance: T, **kwargs: Any) -> None:
        with cls.get_transaction():
            for key, value in kwargs.items():
                setattr(instance, key, value)

    @classmethod
    def delete_by_id(cls, id: Any) -> None:
        with cls.get_transaction() as session:
            session.execute(delete(cls._model).where(cls._model.id == id))
