import logging
from typing import Any, Protocol, ClassVar

import niquests
import orjson
from aiohttp import ClientResponse, ClientSession

logger = logging.getLogger()


class ApiError(Exception):
    def __init__(self, name, response):
        self.name = name
        self.response = response

    def __str__(self):
        return (
            f"{self.__class__.__name__}: {self.name} {self.response.status} {self.response.reason} {self.response.text}"
        )


class ServerError(ApiError):
    def __init__(self, response, response_data):
        self.response = response
        self.response_data = response_data


class ClientError(ApiError):
    def __init__(self, response, code, message, detail):
        self.response = response
        self.code = code
        self.message = message
        self.detail = detail

    def __str__(self):
        return f"{self.__class__.__name__}: {self.code} {self.message}{f' - {self.detail}' if self.detail else ''}"


class AsyncApi:
    ApiError = ApiError
    ServerError = ServerError
    ClientError = ClientError

    def __init__(
        self,
        api_root: str,
        headers: dict | None = None,
        settings: dict | None = None,
        session: ClientSession | None = None,
    ):
        self.api_root = api_root
        self.settings = settings or {}
        self.headers = headers or {}
        self.session = session

    async def call_endpoint(
        self,
        resource: str,
        method: str = "GET",
        params: dict | None = None,
        headers: dict | None = None,
        data: dict | list | None = None,
        json: dict | list | None = None,
        settings: dict | None = None,
        session: ClientSession | None = None,
    ) -> Any:
        url = self.api_root
        if resource:
            url = f"{self.api_root}/{resource}"
        headers = self.headers | (headers or {})
        settings = self.settings | (settings or {})

        async with session or self.session or ClientSession() as session:
            async with session.request(
                method, url, params=params, data=data, json=json, headers=headers, **settings
            ) as response:
                return await self.process_response(response)

    async def response_to_native(self, response: ClientResponse) -> Any:
        try:
            return await response.json(loads=orjson.loads, content_type=None)
        except ValueError:
            return await response.text()

    def error_handling(self, response: ClientResponse, response_data: Any) -> bool | None:
        if 200 <= response.status < 300:
            return None

        elif 400 <= response.status < 500:
            raise self.ClientError(response, response.status, response.reason, response_data)

        elif response.status >= 500:
            raise self.ServerError(response, response_data)

        else:
            return False

    async def process_response(self, response: ClientResponse) -> Any:
        response_data = await self.response_to_native(response)

        if self.error_handling(response, response_data) is False:
            raise self.ApiError("UnknownError", response)

        return response_data


class SyncApi:
    ApiError = ApiError
    ServerError = ServerError
    ClientError = ClientError

    def __init__(
        self,
        api_root: str,
        headers: dict | None = None,
        settings: dict | None = None,
        session: niquests.Session | None = None,
    ):
        self.api_root = api_root
        self.settings = settings or {}
        self.headers = headers or {}
        self.session = session

    def call_endpoint(
        self,
        resource: str,
        method: str = "GET",
        params: dict | None = None,
        headers: dict | None = None,
        data: dict | list | None = None,
        json: dict | list | None = None,
        settings: dict | None = None,
        session: niquests.Session | None = None,
    ) -> Any:
        url = self.api_root
        if resource:
            url = f"{self.api_root}/{resource}"

        headers = {**self.headers, **(headers or {})}
        settings = {**self.settings, **(settings or {})}

        with session or self.session or niquests.Session() as sess:
            response = sess.request(method, url, params=params, data=data, json=json, headers=headers, **settings)
            return self.process_response(response)

    def response_to_native(self, response: niquests.Response) -> Any:
        if not response.content:
            return response.text

        try:
            return orjson.loads(response.content)
        except ValueError:
            return response.text

    def error_handling(self, response: niquests.Response, response_data: Any) -> bool | None:
        if response.status_code is None:
            raise self.ApiError("Not response status", response)

        if 200 <= response.status_code < 300:
            return None

        elif 400 <= response.status_code < 500:
            raise self.ClientError(response, response.status_code, response.reason, response_data)

        elif response.status_code >= 500:
            raise self.ServerError(response, response_data)

        else:
            return False

    def process_response(self, response: niquests.Response) -> Any:
        response_data = self.response_to_native(response)

        if self.error_handling(response, response_data) is False:
            raise self.ApiError("UnknownError", response)

        return response_data


class IClient(Protocol):
    """
    class MyClient:
        Api = AsyncApi
        api_root = "http://example.com/api"

        def __init__(
            self,
            token: str,
            headers: dict | None = None,
            settings: dict | None = None,
            session: ClientSession | None = None,
        ):
            headers = {"Authorization": f"Bearer {token}"}
            self.api = self.Api(self.api_root, headers, settings, session)

        async def my_endpoint():
            return await self.api.call_endpoint("resource_name", "POST")

    client = MyClient("token")
    await client.my_endpoint()
    """

    Api: ClassVar[type[AsyncApi | SyncApi]]
    api_root: str
    api: AsyncApi | SyncApi
