import datetime

from freezegun import freeze_time

from project.container import DIContainer, Container
from tests.factories import UserFactory


@freeze_time("2025-01-01")
def test_question_use_case(session):
    """Тест UseCase для задавания вопроса в чат."""

    class MockLLMClient:
        """Мок LLM клиента для тестирования."""

        def invoke(self, messages, config=None):
            """Возвращает мок-ответ."""

            class Response:
                content = f"Bar {datetime.date.today()}"

            return Response()

    user = UserFactory()

    container = DIContainer(llm_client=MockLLMClient())

    answer = container.chat.ask(user_id=user.id, question="Foo")

    assert answer == "Bar 2025-01-01"


@freeze_time("2025-01-01")
def test_question_use_case_with_chat_id(session):
    """Тест UseCase для задавания вопроса в конкретный чат."""

    class MockLLMClient:
        """Мок LLM клиента для тестирования."""

        def invoke(self, messages, config=None):
            """Возвращает мок-ответ."""

            class Response:
                content = f"Bar {datetime.date.today()}"

            return Response()

    user = UserFactory()

    container = DIContainer(llm_client=MockLLMClient())

    # Создаем чат
    chat_id = container.chat.create_chat(user_id=user.id, title="Test Chat")

    # Задаем вопрос в конкретный чат
    answer = container.chat.ask(user_id=user.id, question="Foo", chat_id=chat_id)

    assert answer == "Bar 2025-01-01"


@freeze_time("2025-01-01")
def test_question_use_case_with_http_mock(session, httpx_responses):
    """Тест UseCase для задавания вопроса в чат."""

    # Mock the LLM API responses - we need multiple responses since the agent makes several calls
    response_text = "Bar"

    mock_response_json = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "choices": [
            {
                "message": {"role": "assistant", "content": response_text},
                "finish_reason": "stop",
                "index": 0,
            },
        ],
        "usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7},
        "created": 1234567890,
        "model": "gpt-4o-mini",
    }

    # Мок HTTP запроса.
    httpx_responses.add(
        method="POST",
        url="https://api.openai.com/v1/chat/completions",
        json=mock_response_json,
        status=200,
    )

    user = UserFactory()

    answer = Container().chat.ask(user_id=user.id, question="Foo")

    assert answer == response_text


def test_create_chat_use_case(session):
    """Тест создания нового чата."""
    user = UserFactory()

    container = Container()

    chat_id = container.chat.create_chat(user_id=user.id, title="Test Chat")

    assert chat_id is not None


def test_get_active_chat_use_case(session):
    """Тест получения активного чата."""
    user = UserFactory()

    container = Container()

    # Первый вызов должен создать чат
    chat_id1 = container.chat.get_active_chat(user_id=user.id)

    # Второй вызов должен вернуть тот же чат
    chat_id2 = container.chat.get_active_chat(user_id=user.id)

    assert chat_id1 == chat_id2
