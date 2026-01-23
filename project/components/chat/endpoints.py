from fastapi import APIRouter

from project.components.base.schemas import ApiResponseSchema
from project.components.chat.schemas import (
    AskBodySchema,
    ChatHistoryBodySchema,
    ChatHistoryResponseSchema,
    CreateChatBodySchema,
    CreateChatResponseSchema,
)
from project.container import Container
from project.datatypes import AnswerT

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/v1/create", response_model=ApiResponseSchema[CreateChatResponseSchema])
def create_chat_v1(body: CreateChatBodySchema):
    """Create a new chat."""
    chat_id = Container().chat.create_chat(user_id=body.user_id, title=body.title)
    return ApiResponseSchema(
        data=CreateChatResponseSchema(
            chat_id=chat_id,
            title=body.title or "Новый чат",
        )
    )


@router.post("/v1/history", response_model=ApiResponseSchema[ChatHistoryResponseSchema])
def get_history_v1(body: ChatHistoryBodySchema):
    """Get chat history for a user."""
    history = Container().chat.get_history(
        user_id=body.user_id,
        chat_id=body.chat_id,
        limit=body.limit,
    )
    return ApiResponseSchema(data=ChatHistoryResponseSchema(messages=history))


@router.post("/v1/ask", response_model=ApiResponseSchema[AnswerT])
def ask_v1(body: AskBodySchema):
    """Asking a question to the chat."""
    answer = Container().chat.ask(
        user_id=body.user_id,
        question=body.question,
        chat_id=body.chat_id,
    )
    return ApiResponseSchema(data=answer)
