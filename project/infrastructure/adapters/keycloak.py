import project.exceptions
import project.infrastructure.exceptions
from project.infrastructure.adapters import base_client as base


class KeycloakApiError(project.exceptions.ApiError):
    pass


class KeycloakServerError(project.exceptions.ServerError):
    pass


class KeycloakClientError(project.exceptions.ClientError):
    pass


class KeycloakAsyncClient:
    class Api(base.AsyncApi):
        ApiError = KeycloakApiError
        ServerError = KeycloakServerError
        ClientError = KeycloakClientError

    def __init__(
        self,
        keycloak_url: str,
        client_id: str,
        username: str | None = None,
        password: str | None = None,
    ):
        self.api_root = keycloak_url
        self.api = self.Api(self.api_root)
        self._auth_data = {
            "grant_type": "password",
            "client_id": client_id,
            "username": username,
            "password": password,
        }

    async def get_token(self) -> str:
        response = await self.api.call_endpoint(
            "",
            method="POST",
            data=self._auth_data,
        )
        if "access_token" in response:
            return response["access_token"]

        error_msg = "No access token in response"
        raise KeycloakApiError(error_msg, response)


class KeycloakSyncClient:
    class Api(base.SyncApi):
        ApiError = KeycloakApiError
        ServerError = KeycloakServerError
        ClientError = KeycloakClientError

    def __init__(
        self,
        keycloak_url: str,
        client_id: str,
        username: str | None = None,
        password: str | None = None,
    ):
        self.api_root = keycloak_url
        self.api = self.Api(self.api_root)
        self._auth_data = {
            "grant_type": "password",
            "client_id": client_id,
            "username": username,
            "password": password,
        }

    def get_token(self) -> str:
        response = self.api.call_endpoint(
            "",
            method="POST",
            data=self._auth_data,
        )
        if "access_token" in response:
            return response["access_token"]

        error_msg = "No access token in response"
        raise KeycloakApiError(error_msg, response)
