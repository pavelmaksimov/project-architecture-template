from pydantic import BaseModel, Field

from project.datatypes import UserIdT, QuestionT, AnswerT


class AskBodySchema(BaseModel):
    """Схема для запроса вопроса в чат."""

    user_id: UserIdT
    question: QuestionT = Field(..., min_length=1, max_length=10000, description="Текст вопроса")


class ChatHistoryBodySchema(BaseModel):
    user_id: UserIdT
    limit: int = 20


class ChatHistoryItemSchema(BaseModel):
    """Схема для элемента истории чата."""

    question: QuestionT
    answer: AnswerT


class ChatHistoryResponseSchema(BaseModel):
    messages: list[ChatHistoryItemSchema]
