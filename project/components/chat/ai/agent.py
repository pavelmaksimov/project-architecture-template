import typing as t

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from project.components.chat.ai.prompts import SYSTEM_PROMPT
from project.components.chat.enums import MessageTypeEnum
from project.datatypes import QuestionT, AnswerT

if t.TYPE_CHECKING:
    from project.components.chat.models import MessageModel
    from langchain_openai import ChatOpenAI


class ChatAgent:
    def __init__(self, llm_client: "ChatOpenAI"):
        self.llm_client = llm_client

    def generate_answer(self, question: QuestionT, history: list["MessageModel"]) -> AnswerT:
        """
        Получить ответ от LLM на основе вопроса и истории чата.

        Returns:
            Текст ответа от AI
        """
        # Подготовить сообщения для LangChain
        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        # Добавить историю
        for msg in history:
            if msg.message_type == MessageTypeEnum.USER:
                messages.append(HumanMessage(content=msg.content))
            elif msg.message_type == MessageTypeEnum.AI:
                messages.append(AIMessage(content=msg.content))

        # Добавить текущий вопрос
        messages.append(HumanMessage(content=question))

        # Получить ответ от LLM
        response = self.llm_client.invoke(messages)

        return AnswerT(response.content)
