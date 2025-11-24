import factory

from project.components.user.models import UserModel
from project.infrastructure.adapters.database import scoped_session_factory
from project.components.chat.models import MessageModel
from project.components.chat.enums import MessageTypeEnum


class SQLAlchemyFactoryMeta:
    sqlalchemy_session_factory = lambda: scoped_session_factory()
    sqlalchemy_session = None
    sqlalchemy_session_persistence = "flush"


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta(SQLAlchemyFactoryMeta):
        model = UserModel

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("name")
    telegram_user_id = factory.Sequence(lambda n: n + 1)
    telegram_username = factory.Faker("name")
    is_admin = False


class MessageFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Фабрика для создания сообщений чата."""

    class Meta(SQLAlchemyFactoryMeta):
        model = MessageModel

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.SelfAttribute("user.id")
    content = factory.Faker("text", max_nb_chars=50)
    message_type = MessageTypeEnum.USER

    user = factory.SubFactory(UserFactory)
