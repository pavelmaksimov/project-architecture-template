from sqlalchemy import BigInteger, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from project.components.base.models import TimeMixin, Base


class UserModel(TimeMixin, Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)
    telegram_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
