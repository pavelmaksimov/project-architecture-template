from tests.factories import UserFactory, MessageFactory
from project.components.chat.enums import MessageTypeEnum


class TestChatHistory:
    def test_get_history_success(self, api_client):
        """Тест получения истории чата."""
        user = UserFactory()

        # Создаем первую пару вопрос-ответ
        MessageFactory(content="Test question", user=user, message_type=MessageTypeEnum.USER)
        MessageFactory(content="Test answer", user=user, message_type=MessageTypeEnum.AI)

        # Создаем вторую пару вопрос-ответ
        MessageFactory(content="Test question 2", user=user, message_type=MessageTypeEnum.USER)
        MessageFactory(content="Test answer 2", user=user, message_type=MessageTypeEnum.AI)

        response = api_client.post("/chat/v1/history", json={"user_id": user.id})

        assert response.status_code == 200
        assert response.json() == {
            "data": {
                "messages": [
                    {"question": "Test question", "answer": "Test answer"},
                    {"question": "Test question 2", "answer": "Test answer 2"},
                ],
            },
        }

    def test_empty_history(self, api_client):
        """Тест пустой истории чата."""
        response = api_client.post("/chat/v1/history", json={"user_id": 0})

        assert response.status_code == 200
        assert response.json() == {"data": {"messages": []}}
