from fastapi import APIRouter

from project.components.base.schemas import ApiResponseSchema
from project.components.chat.schemas import AskBodySchema, ChatHistoryBodySchema, ChatHistoryResponseSchema
from project.container import Container
from project.datatypes import AnswerT

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/v1/history", response_model=ApiResponseSchema[ChatHistoryResponseSchema])
def get_history_v1(body: ChatHistoryBodySchema):
    """Get chat history for a user."""
    history = Container().chat.get_history(user_id=body.user_id, limit=body.limit)
    return ApiResponseSchema(data=ChatHistoryResponseSchema(messages=history))


@router.post("/v1/ask", response_model=ApiResponseSchema[AnswerT])
def ask_v1(body: AskBodySchema):
    """Asking a question to the chat."""
    answer = Container().chat.ask(user_id=body.user_id, question=body.question)
    return ApiResponseSchema(data=answer)
