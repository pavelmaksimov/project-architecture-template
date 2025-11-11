def test_unauthorized_access(api_client):
    response = api_client.get("/chat/v1/history/1", headers={"Api-Token": "invalid_token"})

    assert response.status_code == 401
    assert "invalid token" in response.text.lower()
