import pytest

from project.infrastructure.adapters.keycloak import KeycloakServerError, KeycloakClientError


def test_keycloak_sync_client_get_token_success(keycloak_client, mock_keycloak):
    token = keycloak_client.get_token()

    assert token == "test_token"


def test_keycloak_sync_client_get_token_failure(httpx_responses, keycloak_client):
    httpx_responses.add(
        "POST",
        "http://keycloak.example.com/auth",
        json={"error": "invalid_grant"},
        status_code=400,
    )

    with pytest.raises(KeycloakClientError):
        keycloak_client.get_token()


def test_keycloak_sync_client_server_error(httpx_responses, keycloak_client):
    httpx_responses.add(
        "POST",
        "http://keycloak.example.com/auth",
        json={"error": "internal_server_error"},
        status_code=500,
    )

    with pytest.raises(KeycloakServerError):
        keycloak_client.get_token()


@pytest.mark.asyncio
async def test_keycloak_async_client_get_token_success(mock_async_keycloak, keycloak_aclient):
    token = await keycloak_aclient.get_token()

    assert token == "test_token"


@pytest.mark.asyncio
async def test_keycloak_async_client_get_token_failure(aiohttp_responses, keycloak_aclient):
    aiohttp_responses.add(
        "http://keycloak.example.com/auth",
        method="POST",
        payload={"error": "invalid_grant"},
        status=400,
    )

    with pytest.raises(KeycloakClientError):
        await keycloak_aclient.get_token()


@pytest.mark.asyncio
async def test_keycloak_async_client_server_error(aiohttp_responses, keycloak_aclient):
    aiohttp_responses.add(
        "http://keycloak.example.com/auth",
        method="POST",
        payload={"error": "internal_server_error"},
        status=500,
    )

    with pytest.raises(KeycloakServerError):
        await keycloak_aclient.get_token()
