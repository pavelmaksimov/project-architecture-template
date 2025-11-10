from functools import cache

from llm_common.clients.auth_client import AuthHttpClient

from project.infrastructure.adapters.base_client import IClient, AsyncApi
from project.exceptions import ApiError, ServerError, ClientError
from project.settings import Settings


class AuthApiError(ApiError):
    pass


class AuthServerError(ServerError):
    pass


class AuthClientError(ClientError):
    pass


class AuthClient(IClient):
    class Api(AsyncApi):
        ApiError = AuthApiError
        ServerError = AuthServerError
        ClientError = AuthClientError
        ClientSession = AuthHttpClient

    def __init__(self):
        self.api_root = Settings().BOT_AUTH_SERVICE_URL
        self.api = self.Api(self.api_root, name_for_monitoring="auth_api", request_settings={"timeout": 10})

    async def check_telegram_user(self, user_telegram_id: int) -> bool:
        result = await self.api.call_endpoint(f"api/check/{user_telegram_id}")
        return result["exists"]

    async def get_users_data(self) -> dict:
        return await self.api.call_endpoint("api/users_data")


@cache
def auth_client():
    return AuthClient()  # di: skip
