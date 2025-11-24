def test_unauthorized_access(api_client):
    response = api_client.post("/chat/v1/history", headers={"Api-Token": "invalid_token"})

    assert response.status_code == 401
    assert "invalid token" in response.text.lower()
