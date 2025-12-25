from sqlalchemy import String, BigInteger, Integer, ForeignKey, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from project.components.base.models import TimeMixin, Base
from project.components.user.models import UserModel
from project.components.chat.enums import MessageTypeEnum
from project.datatypes import UserIdT, ChatIdT, MessageIdT


class ChatModel(TimeMixin, Base):
    """Модель для хранения чатов/диалогов пользователей с AI."""

    __tablename__ = "chat"

    id: Mapped[ChatIdT] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[UserIdT] = mapped_column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    user: Mapped[UserModel] = relationship("UserModel")
    messages: Mapped[list["MessageModel"]] = relationship(
        "MessageModel", back_populates="chat", cascade="all, delete-orphan"
    )


class MessageModel(TimeMixin, Base):
    """Модель для хранения сообщений чата (вопросы пользователя и ответы AI)."""

    __tablename__ = "message"

    id: Mapped[MessageIdT] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[ChatIdT] = mapped_column(Integer, ForeignKey("chat.id"), index=True, nullable=False)
    user_id: Mapped[UserIdT] = mapped_column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    message_type: Mapped[MessageTypeEnum] = mapped_column(Enum(MessageTypeEnum), nullable=False)

    chat: Mapped[ChatModel] = relationship("ChatModel", back_populates="messages")
    user: Mapped[UserModel] = relationship("UserModel")
