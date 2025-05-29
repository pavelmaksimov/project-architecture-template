from contextlib import contextmanager
from typing import Generator, Any

from sqlalchemy.orm import Session as ORMSession

from project.domains.chat.repositories import QuestionRepository, AnswerRepository, ChatRepository
from project.domains.user.repository import UserRepository
from project.infrastructure.adapters.database import Transaction, CurrentTransaction
from project.utils.structures import Singleton


class Repositories(metaclass=Singleton):
    def __init__(self):
        self.user = UserRepository()  # di: skip
        self.question = QuestionRepository()  # di: skip
        self.answer = AnswerRepository()  # di: skip
        self.chat = ChatRepository()  # di: skip

    @classmethod
    @contextmanager
    def transaction(cls) -> Generator[ORMSession, Any, None]:
        with Transaction() as session:  # di: skip
            yield session

    @classmethod
    @contextmanager
    def current_transaction(cls) -> Generator[ORMSession, Any, None]:
        with CurrentTransaction() as session:  # di: skip
            yield session
