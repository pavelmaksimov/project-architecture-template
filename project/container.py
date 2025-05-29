from project.domains.user.service import AuthService, QuotaService
from project.domains.chat.interfaces import IGenerateGateway
from project.domains.chat.use_cases import ChatUseCase
from project.domains.chat.service import ChatService
from project.domains.chat.answer.service import AnswerService
from project.infrastructure.container import Repositories
from project.infrastructure.adapters.llm import LLMClient
from project.utils.structures import Singleton


class DIContainer(metaclass=Singleton):
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

    @classmethod
    def clear_cache(cls):
        Singleton._instances.clear()  # di: skip
