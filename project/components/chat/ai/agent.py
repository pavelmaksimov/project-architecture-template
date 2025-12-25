import typing as t

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langfuse import propagate_attributes
from langfuse.langchain import CallbackHandler

from project.components.chat.ai.prompts import SYSTEM_PROMPT
from project.components.chat.enums import MessageTypeEnum
from project.datatypes import QuestionT, AnswerT, UserIdT, ChatIdT

if t.TYPE_CHECKING:
    from project.components.chat.models import MessageModel
    from langchain_openai import ChatOpenAI
    from langfuse import Langfuse


class ChatAgent:
    def __init__(
        self,
        llm_client: "ChatOpenAI",
        langfuse_client: "Langfuse",
    ):
        self.llm_client = llm_client
        self.langfuse_client = langfuse_client

    def generate_answer(
        self, user_id: UserIdT, chat_id: ChatIdT, question: QuestionT, history: list["MessageModel"]
    ) -> AnswerT:
        """
        Получить ответ от LLM на основе вопроса и истории чата.

        Returns:
            Текст ответа от AI
        """
        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        for msg in history:
            if msg.message_type == MessageTypeEnum.USER:
                messages.append(HumanMessage(content=msg.content))
            elif msg.message_type == MessageTypeEnum.AI:
                messages.append(AIMessage(content=msg.content))

        messages.append(HumanMessage(content=question))

        with (
            self.langfuse_client.start_as_current_observation(as_type="span", name="chat"),
            propagate_attributes(user_id=str(user_id), session_id=str(chat_id)),
        ):
            response = self.llm_client.invoke(messages, config=RunnableConfig(callbacks=[CallbackHandler()]))

        return AnswerT(response.content)
