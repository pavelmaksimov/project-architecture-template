from datetime import datetime

from sqlalchemy import func, MetaData
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    declarative_base,
)

public_schema = MetaData()
Base = declarative_base(metadata=public_schema)


class TimeMixin:
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())
