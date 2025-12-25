from contextlib import contextmanager
import typing as t

from project.components.chat.ai.agent import ChatAgent
from project.components.chat.repositories import ChatRepository, MessageRepository
from project.components.chat.use_cases import Chat
from project.components.user.repositories import UserRepository, UserCacheRepository
from project.components.user.service import QuotaService
from project.infrastructure.adapters.database import transaction, current_transaction
from project.infrastructure.adapters.llm import llm_chat_client
from project.libs.structures import LazyInit

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session as ORMSession


class AllRepositories:
    def __init__(self, user_repo=None, user_cache_repo=None, message_repo=None, chat_repo=None):
        self.user = user_repo or UserRepository()  # di: skip
        self.user_cache = user_cache_repo or UserCacheRepository()  # di: skip
        self.message = message_repo or MessageRepository()  # di: skip
        self.chat = chat_repo or ChatRepository()  # di: skip

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

    def __init__(self, repositories=None, llm_client=None, chat_agent=None):
        # Infrastructure dependencies:
        self.repo = repositories or Repositories()  # di: skip
        llm_client = llm_client or llm_chat_client()  # di: skip

        # AI services:
        chat_agent = chat_agent or ChatAgent()  # di: skip

        # Domain Services:
        quota_service = QuotaService()  # di: skip

        # UseCases:
        self.chat = Chat(self.repo, chat_agent, quota_service)  # di: skip


Container = LazyInit(DIContainer)
