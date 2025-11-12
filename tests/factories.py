import factory

from project.components.user.models import UserModel
from project.infrastructure.adapters.database import scoped_session_factory
from project.components.chat.models import QuestionModel, AnswerModel


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


class QuestionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta(SQLAlchemyFactoryMeta):
        model = QuestionModel

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.SelfAttribute("user.id")
    telegram_message_id = factory.Sequence(lambda n: n + 1)
    content = factory.Faker("text", max_nb_chars=50)
    is_voice = False

    user = factory.SubFactory(UserFactory)


class AnswerFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta(SQLAlchemyFactoryMeta):
        model = AnswerModel

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.SelfAttribute("user.id")
    question_id = factory.SelfAttribute("question.id")
    content = factory.Faker("text", max_nb_chars=50)

    user = factory.SubFactory(UserFactory)
    question = factory.SubFactory(QuestionFactory)
