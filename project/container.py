from contextlib import contextmanager
import typing as t

from project.components.chat.answer.service import AnswerService
from project.components.chat.interfaces import IGenerateGateway
from project.components.chat.repositories import QuestionRepository, AnswerRepository, ChatRepository
from project.components.chat.service import ChatService
from project.components.chat.use_cases import ChatUseCase
from project.components.user.repositories import UserRepository
from project.components.user.service import AuthService, QuotaService
from project.infrastructure.adapters.database import transaction, current_transaction
from project.infrastructure.adapters.llm import LLMClient
from project.libs.structures import LazyInit

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session as ORMSession


class AllRepositories:
    def __init__(self):
        self.user = UserRepository()  # di: skip
        self.question = QuestionRepository()  # di: skip
        self.answer = AnswerRepository()  # di: skip
        self.chat = ChatRepository()  # di: skip

    @classmethod
    @contextmanager
    def transaction(cls) -> t.Generator["ORMSession", t.Any, None]:
        with transaction() as session:  # di: skip
            yield session

    @classmethod
    @contextmanager
    def current_transaction(cls) -> t.Generator["ORMSession", t.Any, None]:
        with current_transaction() as session:  # di: skip
            yield session


Repositories = LazyInit(AllRepositories)


class DIContainer:
    """
    This is dependency injection container.
    For resolving dependencies.
    """

    def __init__(self, generate_adapter: IGenerateGateway | None = None):
        # Infrastructure dependencies:
        self.repo = Repositories()  # di: skip
        self._generate_adapter = generate_adapter or LLMClient()  # di: skip

        # Domain dependencies:
        self._answer_service = AnswerService(self._generate_adapter)  # di: skip
        self._chat_service = ChatService(self.repo, self._answer_service)  # di: skip
        self._auth_service = AuthService()  # di: skip
        self._quota_service = QuotaService()  # di: skip

        # Application dependencies:
        self.chat = ChatUseCase(self.repo, self._chat_service, self._auth_service, self._quota_service)  # di: skip


Container = LazyInit(DIContainer)
