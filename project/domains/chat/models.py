from sqlalchemy import String, BigInteger
from sqlalchemy import Integer, ForeignKey, Boolean

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column


from project.domains.base.models import TimeMixin, Base
from project.domains.user.models import User
from project.datatypes import UserIdT, AnswerT, QuestionT


class Question(TimeMixin, Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[UserIdT] = mapped_column(Integer, ForeignKey("users.id"))
    telegram_message_id: Mapped[int] = mapped_column(Integer, nullable=True)
    content: Mapped[QuestionT] = mapped_column(String, nullable=False)
    is_voice: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship("User")


class Answer(TimeMixin, Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[UserIdT] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("questions.id"), index=True)
    content: Mapped[AnswerT] = mapped_column(String, nullable=False)

    user: Mapped[User] = relationship("User")
    question: Mapped["Question"] = relationship("Question")
