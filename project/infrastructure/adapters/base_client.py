import logging
import typing as t
from contextlib import asynccontextmanager

import httpx
import orjson
from aiohttp import ClientResponse, ClientSession, typedefs
from llm_common.clients.aiohttp_client import ClientSessionWithMonitoring
from llm_common.clients.httpx_client import HttpxClientWithMonitoring

from project.infrastructure.exceptions import ApiError, ServerError, ClientError
from project.utils.log import timer

logger = logging.getLogger(__name__)


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
        log_level: int | str = logging.INFO,
    ):
        self.api_root = api_root
        self.settings = settings or {}
        self.headers = headers or {}
        self.session = session
        self.log_level = log_level
        if isinstance(self.log_level, str):
            self.log_level = logging.getLevelNamesMapping()[self.log_level.upper()]

    @asynccontextmanager
    async def Session(self):  # noqa: N802
        if self.session:
            yield self.session
        else:
            async with ClientSessionWithMonitoring() as session:
                yield session

    async def call_endpoint(
        self,
        resource: str,
        method: str = "GET",
        params: typedefs.Query = None,
        headers: typedefs.LooseHeaders | None = None,
        data: t.Any = None,
        json: t.Any = None,
        settings: dict | None = None,
        session: ClientSession | None = None,
    ) -> t.Any:
        url = self.api_root
        if resource:
            url = f"{self.api_root}/{resource}"
        headers = self.headers | (headers or {})
        settings = self.settings | (settings or {})

        async with session or self.session or ClientSessionWithMonitoring() as sess:
            logger.log(self.log_level, "Call endpoint: %s %s", method, url)

            if self.log_level <= logging.DEBUG:
                if headers:
                    logger.debug("Headers: %s", headers)
                if params:
                    logger.debug("Params: %s", params)
                if data:
                    logger.debug("Data: %s", data)
                if json:
                    logger.debug("Json: %s", json)

            with timer() as get_elapsed:
                async with sess.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    json=json,
                    headers=headers,
                    **settings,
                ) as response:
                    elapsed = get_elapsed()
                    logger.debug("End call endpoint: %s %s, duration %s ", method, url, elapsed)

                    return await self.process_response(response)

    async def response_to_native(self, response: ClientResponse) -> t.Any:
        try:
            return await response.json(loads=orjson.loads, content_type=None)
        except ValueError:
            return await response.text()

    async def error_handling(self, response: ClientResponse, response_data: t.Any) -> None:
        if 200 <= response.status < 300:
            return

        if 400 <= response.status < 500:
            raise self.ClientError(response, response.status, response.reason, response_data)

        if response.status >= 500:
            raise self.ServerError(response, response_data)

        raise self.ApiError(response_data, response)

    async def process_response(self, response: ClientResponse) -> t.Any:
        response_data = await self.response_to_native(response)
        await self.error_handling(response, response_data)
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
        session: httpx.Client | None = None,
        log_level: int | str = logging.INFO,
    ):
        self.api_root = api_root
        self.settings = settings or {}
        self.headers = headers or {}
        self.session = session
        self.log_level = log_level
        if isinstance(self.log_level, str):
            self.log_level = logging.getLevelNamesMapping()[self.log_level.upper()]

    def call_endpoint(
        self,
        resource: str,
        method: str = "GET",
        params: dict | None = None,
        headers: dict | None = None,
        data: t.Any = None,
        json: t.Any = None,
        settings: dict | None = None,
        session: httpx.Client | None = None,
    ) -> t.Any:
        url = self.api_root
        if resource:
            url = f"{self.api_root}/{resource}"

        headers = self.headers | (headers or {})
        settings = self.settings | (settings or {})

        with session or self.session or HttpxClientWithMonitoring() as sess:
            logger.log(self.log_level, "Call endpoint: %s %s", method, url)

            if self.log_level <= logging.DEBUG:
                if headers:
                    logger.debug("Headers: %s", headers)
                if params:
                    logger.debug("Params: %s", params)
                if data:
                    logger.debug("Data: %s", data)
                if json:
                    logger.debug("Json: %s", json)

            response = sess.request(method, url, params=params, data=data, json=json, headers=headers, **settings)

            logger.debug("End call endpoint: %s %s, duration %s ", method, url, response.elapsed)

            return self.process_response(response)

    def response_to_native(self, response: httpx.Response) -> t.Any:
        try:
            return orjson.loads(response.content)
        except ValueError:
            return response.text

    def error_handling(self, response: httpx.Response, response_data: t.Any) -> None:
        if 200 <= response.status_code < 300:
            return

        if 400 <= response.status_code < 500:
            raise self.ClientError(response, response.status_code, response.reason_phrase, response_data)

        if response.status_code >= 500:
            raise self.ServerError(response, response_data)

        raise self.ApiError(response_data, response)

    def process_response(self, response: httpx.Response) -> t.Any:
        response_data = self.response_to_native(response)
        self.error_handling(response, response_data)
        return response_data


class IClient(t.Protocol):
    """
    class MyClient:
        Api = AsyncApi
        api_root = "http://example.com/api"
        name_for_monitoring = "servicename_api"

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

    # with session
    async with client.api.Session():
        await client.my_endpoint()
    """

    Api: t.ClassVar[type[AsyncApi | SyncApi]]
    api_root: str
    api: AsyncApi | SyncApi
    name_for_monitoring: str
