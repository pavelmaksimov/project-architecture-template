import project.infrastructure.exceptions
from project.utils import base_client as base


class KeycloakApiError(project.infrastructure.exceptions.ApiError):
    pass


class KeycloakServerError(project.infrastructure.exceptions.ServerError):
    pass


class KeycloakClientError(project.infrastructure.exceptions.ClientError):
    pass


class KeycloakAsyncApi(base.AsyncApi):
    ApiError = KeycloakApiError
    ServerError = KeycloakServerError
    ClientError = KeycloakClientError


class KeycloakSyncApi(base.SyncApi):
    ApiError = KeycloakApiError
    ServerError = KeycloakServerError
    ClientError = KeycloakClientError


class KeycloakAsyncClient:
    Api = KeycloakAsyncApi

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
    Api = KeycloakSyncApi

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
