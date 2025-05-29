from tests.factories import UserFactory, QuestionFactory, AnswerFactory


class TestChatHistory:
    def test_get_history_success(self, api_client):
        user = UserFactory()
        question = QuestionFactory.create(content="Test question", user=user)
        AnswerFactory(content="Test answer", user=user, question=question)

        question2 = QuestionFactory(content="Test question 2", user=user)
        AnswerFactory(content="Test answer 2", user=user, question=question2)

        response = api_client.get(f"/chat/v1/history/{user.id}")

        assert response.status_code == 200
        assert response.json() == [
            {"question": "Test question", "answer": "Test answer"},
            {"question": "Test question 2", "answer": "Test answer 2"},
        ]

    def test_empty_history(self, api_client):
        response = api_client.get("/chat/v1/history/0?limit=10")

        assert response.status_code == 200
        assert response.json() == []

    def test_invalid_limit_parameter(self, api_client):
        response = api_client.get("/chat/v1/history/1?limit=0")

        assert response.status_code == 422
        assert "limit" in response.text.lower()
