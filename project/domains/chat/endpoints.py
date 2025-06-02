from fastapi import APIRouter, Query

from project.domains.base.schemas import BaseResponse
from project.domains.chat.schemas import AskBody
from project.container import Container

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/v1/history/{user_id}")
def get_chat_history_v1(
    user_id: int,
    limit: int = Query(default=10, ge=1),
):
    """Getting the story of a user chat."""
    return Container().repo.chat.get_history(user_id=user_id, limit=limit)


@router.post("/v1/ask", response_model=BaseResponse[str])
def ask_v1(body: AskBody):
    """Asking a question to the chat."""
    message = Container().chat.ask(user_id=body.user_id, question=body.question)

    return message
