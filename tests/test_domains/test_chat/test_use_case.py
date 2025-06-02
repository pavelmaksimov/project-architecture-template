import datetime

from freezegun import freeze_time

from project.container import DIContainer
from tests.factories import UserFactory


@freeze_time("2025-01-01")
def test_question_use_case(session):
    class GenerateAdapter:
        def generate(self, messages: list[str]):
            return f"Bar {datetime.date.today()}"

    user = UserFactory()

    container = DIContainer(generate_adapter=GenerateAdapter())

    answer = container.chat.ask(user_id=user.id, question="Foo")

    assert answer == "Bar 2025-01-01"
