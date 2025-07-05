from itertools import chain
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from project.domains.chat.interfaces import IGenerateGateway
    from project.domains.chat.models import Question


class AnswerService:
    PROMPT = "Answer the following question: {text}"

    def __init__(self, generate_adapter: "IGenerateGateway"):
        self.generate_adapter = generate_adapter

    def make(self, question: "Question", chat_history) -> str:
        message = self.PROMPT.format(text=question.content)
        content = self.generate_adapter.generate(chain([chat_history], message))

        return content
