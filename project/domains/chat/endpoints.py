from fastapi import APIRouter, Query

from project.domains.base.schemas import BaseResponse
from project.domains.chat.schemas import AskBody
from project.container import DIContainer

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/v1/history/{user_id}")
def get_chat_history_v1(
    user_id: int,
    limit: int = Query(default=10, ge=1),
):
    """Getting the story of a user chat."""
    container = DIContainer()
    return container.repo.chat.get_history(user_id=user_id, limit=limit)


@router.post("/v1/ask", response_model=BaseResponse[str])
def ask_v1(body: AskBody):
    """Asking a question to the chat."""
    container = DIContainer()
    message = container.chat.ask(user_id=body.user_id, question=body.question)

    return message
