import pytest

from project.infrastructure.adapters.keycloak import KeycloakServerError, KeycloakClientError


def test_keycloak_sync_client_get_token_success(keycloak_client, mock_keycloak):
    token = keycloak_client.get_token()

    assert token == "test_token"


def test_keycloak_sync_client_get_token_failure(responses, keycloak_client):
    responses.add(
        responses.POST,
        "http://keycloak.example.com/auth",
        json={"error": "invalid_grant"},
        status=400,
    )

    with pytest.raises(KeycloakClientError):
        keycloak_client.get_token()


def test_keycloak_sync_client_server_error(responses, keycloak_client):
    responses.add(
        responses.POST,
        "http://keycloak.example.com/auth",
        json={"error": "internal_server_error"},
        status=500,
    )

    with pytest.raises(KeycloakServerError):
        keycloak_client.get_token()


@pytest.mark.asyncio
async def test_keycloak_async_client_get_token_success(mock_async_keycloak, keycloak_aclient):
    token = await keycloak_aclient.get_token()

    assert token == "test_token"


@pytest.mark.asyncio
async def test_keycloak_async_client_get_token_failure(aresponses, keycloak_aclient):
    aresponses.add(
        "http://keycloak.example.com/auth",
        method="POST",
        payload={"error": "invalid_grant"},
        status=400,
    )

    with pytest.raises(KeycloakClientError):
        await keycloak_aclient.get_token()


@pytest.mark.asyncio
async def test_keycloak_async_client_server_error(aresponses, keycloak_aclient):
    aresponses.add(
        "http://keycloak.example.com/auth",
        method="POST",
        payload={"error": "internal_server_error"},
        status=500,
    )

    with pytest.raises(KeycloakServerError):
        await keycloak_aclient.get_token()
