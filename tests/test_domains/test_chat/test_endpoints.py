from tests.factories import UserFactory, MessageFactory, ChatFactory
from project.components.chat.enums import MessageTypeEnum


class TestChatEndpoints:
    def test_create_chat_success(self, api_client):
        """Тест создания нового чата."""
        user = UserFactory()

        response = api_client.post("/chat/v1/create", json={"user_id": user.id, "title": "Test Chat"})

        assert response.status_code == 200
        assert "chat_id" in response.json()["data"]
        assert response.json()["data"]["title"] == "Test Chat"

    def test_create_chat_without_title(self, api_client):
        """Тест создания чата без названия."""
        user = UserFactory()

        response = api_client.post("/chat/v1/create", json={"user_id": user.id})

        assert response.status_code == 200
        assert "chat_id" in response.json()["data"]
        assert response.json()["data"]["title"] == "Новый чат"


class TestChatHistory:
    def test_get_history_success(self, api_client):
        """Тест получения истории чата."""
        user = UserFactory()
        chat = ChatFactory(user=user)

        # Создаем первую пару вопрос-ответ в одном чате
        MessageFactory(content="Test question", user=user, chat=chat, message_type=MessageTypeEnum.USER)
        MessageFactory(content="Test answer", user=user, chat=chat, message_type=MessageTypeEnum.AI)

        # Создаем вторую пару вопрос-ответ в том же чате
        MessageFactory(content="Test question 2", user=user, chat=chat, message_type=MessageTypeEnum.USER)
        MessageFactory(content="Test answer 2", user=user, chat=chat, message_type=MessageTypeEnum.AI)

        response = api_client.post(
            "/chat/v1/history",
            json={"user_id": user.id, "chat_id": chat.id}
        )

        assert response.status_code == 200
        assert response.json() == {
            "data": {
                "messages": [
                    {"question": "Test question", "answer": "Test answer"},
                    {"question": "Test question 2", "answer": "Test answer 2"},
                ],
            },
        }

    def test_get_history_without_chat_id(self, api_client):
        """Тест получения истории без указания chat_id."""
        user = UserFactory()
        chat = ChatFactory(user=user)

        # Создаем пару вопрос-ответ
        MessageFactory(content="Test question", user=user, chat=chat, message_type=MessageTypeEnum.USER)
        MessageFactory(content="Test answer", user=user, chat=chat, message_type=MessageTypeEnum.AI)

        response = api_client.post(
            "/chat/v1/history",
            json={"user_id": user.id}
        )

        assert response.status_code == 200
        assert "messages" in response.json()["data"]

    def test_empty_history(self, api_client):
        """Тест пустой истории чата."""
        response = api_client.post("/chat/v1/history", json={"user_id": 0})

        assert response.status_code == 200
        assert response.json() == {"data": {"messages": []}}


class TestAskEndpoint:
    def test_ask_success(self, api_client, httpx_responses):
        """Тест задавания вопроса в чат."""
        response_text = "Test answer"

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

        # Мок HTTP запроса к OpenAI
        httpx_responses.add(
            method="POST",
            url="https://api.openai.com/v1/chat/completions",
            json=mock_response_json,
            status=200,
        )

        user = UserFactory()

        response = api_client.post(
            "/chat/v1/ask",
            json={"user_id": user.id, "question": "Test question"}
        )

        assert response.status_code == 200
        assert "data" in response.json()

    def test_ask_with_chat_id(self, api_client, httpx_responses):
        """Тест задавания вопроса в конкретный чат."""
        response_text = "Test answer"

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

        # Мок HTTP запроса к OpenAI
        httpx_responses.add(
            method="POST",
            url="https://api.openai.com/v1/chat/completions",
            json=mock_response_json,
            status=200,
        )

        user = UserFactory()
        chat = ChatFactory(user=user)

        response = api_client.post(
            "/chat/v1/ask",
            json={"user_id": user.id, "question": "Test question", "chat_id": chat.id}
        )

        assert response.status_code == 200
        assert "data" in response.json()
