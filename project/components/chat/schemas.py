from pydantic import BaseModel, Field

from project.datatypes import UserIdT, QuestionT, AnswerT, ChatIdT


class CreateChatBodySchema(BaseModel):
    """Схема для создания нового чата."""

    user_id: UserIdT
    title: str | None = Field(default=None, max_length=255, description="Название чата")


class CreateChatResponseSchema(BaseModel):
    """Схема ответа при создании чата."""

    chat_id: ChatIdT
    title: str


class AskBodySchema(BaseModel):
    """Схема для запроса вопроса в чат."""

    user_id: UserIdT
    question: QuestionT = Field(..., min_length=1, max_length=10000, description="Текст вопроса")
    chat_id: ChatIdT | None = Field(default=None, description="ID чата (опционально)")


class ChatHistoryBodySchema(BaseModel):
    """Схема для получения истории чата."""

    user_id: UserIdT
    chat_id: ChatIdT | None = Field(default=None, description="ID чата (опционально)")
    limit: int = 20


class ChatHistoryItemSchema(BaseModel):
    """Схема для элемента истории чата."""

    question: QuestionT
    answer: AnswerT


class ChatHistoryResponseSchema(BaseModel):
    """Схема ответа с историей чата."""

    messages: list[ChatHistoryItemSchema]
