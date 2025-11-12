from sqlalchemy import select

from project.components.base.repositories import ORMModelRepository
from project.components.chat.models import MessageModel
from project.components.chat.enums import MessageTypeEnum
from project.datatypes import UserIdT, QuestionT, AnswerT


class MessageRepository(ORMModelRepository[MessageModel]):
    """Репозиторий для работы с сообщениями чата."""

    _model = MessageModel

    @classmethod
    def get_chat_history(cls, user_id: UserIdT, limit: int = 10) -> list[MessageModel]:
        """Получить историю чата пользователя."""
        with cls.get_session() as session:
            query = (
                select(MessageModel)
                .where(MessageModel.user_id == user_id)
                .order_by(MessageModel.created_at.asc())
                .limit(limit)
            )
            return list(session.scalars(query).all())

    @classmethod
    def save_user_message(cls, user_id: UserIdT, content: QuestionT) -> MessageModel:
        """Сохранить сообщение пользователя."""
        return cls.create(user_id=user_id, content=content, message_type=MessageTypeEnum.USER)

    @classmethod
    def save_ai_message(cls, user_id: UserIdT, content: AnswerT) -> MessageModel:
        """Сохранить сообщение AI."""
        return cls.create(user_id=user_id, content=content, message_type=MessageTypeEnum.AI)
