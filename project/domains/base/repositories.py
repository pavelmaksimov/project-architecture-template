from contextlib import contextmanager
import typing as t

from sqlalchemy import select, delete, orm

from project.domains.base.exceptions import NotFoundError, throw
from project.infrastructure.adapters.database import Session, transaction, current_transaction
from project.domains.base.models import Base

T = t.TypeVar("T", bound=Base)


class BaseRepository[T]:
    """
    Separates infrastructure from ORM.
    """

    _model: type[T]

    @classmethod
    @contextmanager
    def get_session(cls) -> t.Generator[orm.Session, t.Any, None]:
        with Session() as session:  # di: skip
            yield session

    @classmethod
    @contextmanager
    def get_transaction(cls) -> t.Generator[orm.Session, t.Any, None]:
        with transaction() as session:  # di: skip
            yield session

    @classmethod
    @contextmanager
    def get_current_transaction(cls) -> t.Generator[orm.Session, t.Any, None]:
        with current_transaction() as session:  # di: skip
            yield session


class Repository[T](BaseRepository):
    """
    Separates infrastructure from ORM.
    """

    @classmethod
    def new(cls, **kwargs: t.Any) -> T:
        return cls._model(**kwargs)

    @classmethod
    def create(cls, **kwargs: t.Any) -> T:
        instance = cls.new(**kwargs)
        cls.save(instance)
        return instance

    @classmethod
    def save(cls, instance: T) -> None:
        with cls.get_transaction() as session:
            session.add(instance)

    @classmethod
    def get_or_none(cls, pk: t.Any) -> T | None:
        with cls.get_session() as session:
            return session.get(cls._model, pk)

    @classmethod
    def get(cls, pk: t.Any) -> T:
        return cls.get_or_none(pk) or throw(NotFoundError, f"{cls._model}.pk", pk)

    @classmethod
    def all(cls):
        with cls.get_session() as session:
            return session.scalars(select(cls._model)).all()

    @classmethod
    def update_fields(cls, instance: T, **kwargs: t.Any) -> None:
        for key, value in kwargs.items():
            setattr(instance, key, value)

    @classmethod
    def update_and_save(cls, instance: T, **kwargs: t.Any) -> None:
        with cls.get_transaction():
            for key, value in kwargs.items():
                setattr(instance, key, value)

    @classmethod
    def delete_by_id(cls, id: t.Any) -> None:
        with cls.get_transaction() as session:
            session.execute(delete(cls._model).where(cls._model.id == id))
