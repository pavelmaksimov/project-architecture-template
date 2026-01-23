from enum import Enum, auto


class MessageTypeEnum(Enum):
    """Тип сообщения в чате."""

    USER = auto()
    INSTRUCTION = auto()
    AI = auto()
