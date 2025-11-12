from itertools import chain
import typing as t

if t.TYPE_CHECKING:
    from project.components.chat.interfaces import IGenerateGateway
    from project.components.chat.models import QuestionModel


class AnswerService:
    PROMPT = "Answer the following question: {text}"

    def __init__(self, generate_adapter: "IGenerateGateway"):
        self.generate_adapter = generate_adapter

    def make(self, question: "QuestionModel", chat_history) -> str:
        message = self.PROMPT.format(text=question.content)
        content = self.generate_adapter.generate(chain([chat_history], message))

        return content
