from sqlalchemy import String, BigInteger, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from project.components.base.models import TimeMixin, Base
from project.components.user.models import UserModel
from project.components.chat.enums import MessageTypeEnum
from project.datatypes import UserIdT


class MessageModel(TimeMixin, Base):
    """Модель для хранения сообщений чата (вопросы пользователя и ответы AI)."""

    __tablename__ = "message"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[UserIdT] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    message_type: Mapped[MessageTypeEnum] = mapped_column(Enum(MessageTypeEnum), nullable=False)

    user: Mapped[UserModel] = relationship("UserModel")
