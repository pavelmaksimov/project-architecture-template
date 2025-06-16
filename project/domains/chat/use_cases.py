from typing import TYPE_CHECKING

from project.datatypes import UserIdT, QuestionT, AnswerT

if TYPE_CHECKING:
    from project.domains.chat.service import ChatService
    from project.container import AllRepositories
    from project.domains.user.service import AuthService, QuotaService


class ChatUseCase:
    def __init__(self, repository: "AllRepositories", chat: "ChatService", auth: "AuthService", quota: "QuotaService"):
        self.repo = repository
        self.chat = chat
        self.auth = auth
        self.quota = quota

    def ask(self, user_id: UserIdT, question: QuestionT) -> AnswerT:
        user = self.repo.user.get_or_none(user_id)

        self.auth.check(user_id)
        self.quota.check(user_id)

        answer = self.chat.make_answer(user.id, question)

        return answer.content
