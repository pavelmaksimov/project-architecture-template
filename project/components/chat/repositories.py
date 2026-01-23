from sqlalchemy import select

from project.components.base.repositories import ORMModelRepository
from project.components.chat.models import ChatModel, MessageModel
from project.components.chat.enums import MessageTypeEnum
from project.datatypes import UserIdT, QuestionT, AnswerT, ChatIdT


class ChatRepository(ORMModelRepository[ChatModel]):
    """Репозиторий для работы с чатами."""

    _model = ChatModel

    @classmethod
    def get_or_create_active_chat(cls, user_id: UserIdT) -> ChatModel:
        """Получить или создать активный чат для пользователя."""
        with cls.get_session() as session:
            # Ищем активный чат
            query = (
                select(ChatModel)
                .where(ChatModel.user_id == user_id)
                .where(ChatModel.is_active.is_(True))
                .order_by(ChatModel.created_at.desc())
                .limit(1)
            )
            chat = session.scalars(query).first()

            # Если чат не найден, создаем новый
            if not chat:
                chat = cls.create(
                    user_id=user_id,
                    title="Новый чат",
                    is_active=True,
                )

            return chat

    @classmethod
    def get_chat_by_id(cls, chat_id: ChatIdT) -> ChatModel | None:
        """Получить чат по ID."""
        with cls.get_session() as session:
            return session.get(ChatModel, chat_id)

    @classmethod
    def deactivate_chat(cls, chat_id: ChatIdT) -> None:
        """Деактивировать чат."""
        with cls.get_current_transaction() as session:
            chat = session.get(ChatModel, chat_id)
            if chat:
                chat.is_active = False


class MessageRepository(ORMModelRepository[MessageModel]):
    """Репозиторий для работы с сообщениями чата."""

    _model = MessageModel

    @classmethod
    def get_chat_history(cls, user_id: UserIdT, chat_id: ChatIdT | None = None, limit: int = 10) -> list[MessageModel]:
        """Получить историю чата пользователя."""
        with cls.get_session() as session:
            query = select(MessageModel)

            # Фильтруем по чату или по пользователю
            if chat_id:
                query = query.where(MessageModel.chat_id == chat_id)
            else:
                query = query.where(MessageModel.user_id == user_id)

            query = query.order_by(MessageModel.created_at.asc()).limit(limit)
            return list(session.scalars(query).all())

    @classmethod
    def save_user_message(cls, user_id: UserIdT, chat_id: ChatIdT, content: QuestionT) -> MessageModel:
        """Сохранить сообщение пользователя."""
        return cls.create(
            user_id=user_id,
            chat_id=chat_id,
            content=content,
            message_type=MessageTypeEnum.USER,
        )

    @classmethod
    def save_ai_message(cls, user_id: UserIdT, chat_id: ChatIdT, content: AnswerT) -> MessageModel:
        """Сохранить сообщение AI."""
        return cls.create(
            user_id=user_id,
            chat_id=chat_id,
            content=content,
            message_type=MessageTypeEnum.AI,
        )
