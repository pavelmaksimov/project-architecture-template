import typing as t

from project.settings import Settings
from project.datatypes import UserIdT, QuestionT

if t.TYPE_CHECKING:
    from project.container import AllRepositories
    from project.domains.chat.models import Answer
    from project.domains.chat.answer.service import AnswerService


class ChatService:
    def __init__(self, repository: "AllRepositories", answer_service: "AnswerService"):
        self.repo = repository
        self.answer_service = answer_service

    def make_answer(self, user_id: UserIdT, question_text: QuestionT) -> "Answer":
        chat_history = self.repo.chat.get_history(user_id, limit=Settings().HISTORY_WINDOW)
        question = self.repo.question.create(user_id=user_id, content=question_text)
        content = self.answer_service.make(question, chat_history)
        answer = self.repo.answer.create(user_id=user_id, question_id=question.id, content=content)

        return answer
