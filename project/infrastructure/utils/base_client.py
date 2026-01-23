import logging
import time
import typing as t
from contextlib import asynccontextmanager, contextmanager

import httpx
import orjson
from aiohttp import ClientResponse, ClientSession, ClientError as AiohttpClientError, typedefs
from llm_common.prometheus import is_build_metrics, http_tracking

from project.exceptions import ExternalApiError, ServerError, ClientError, ExternalHTTPConnectionError

logger = logging.getLogger(__name__)


class AsyncApi:
    ApiError = ExternalApiError
    ServerError = ServerError
    ClientError = ClientError
    ConnectionError = ExternalHTTPConnectionError
    ClientSession = ClientSession
    name_for_monitoring: str

    def __init__(
        self,
        api_root: str,
        *,
        name_for_monitoring: str,
        headers: dict | None = None,
        request_settings: dict | None = None,
        log_level: int | str = logging.INFO,
        logging_extra_data: bool = False,
    ):
        self.api_root = api_root
        self.name_for_monitoring = name_for_monitoring
        self.request_settings = request_settings or {}
        self.headers = headers or {}
        self.logging_extra_data = logging_extra_data
        self.log_level = log_level
        if isinstance(self.log_level, str):
            self.log_level = logging.getLevelNamesMapping()[self.log_level.upper()]
        self.session = None

    @asynccontextmanager
    async def Session(self, **session_settings):  # noqa: N802
        if self.session:
            yield self.session
        else:
            try:
                async with self.ClientSession(**session_settings) as session:
                    self.session = session
                    yield session
            finally:
                self.session = None

    async def call_endpoint(
        self,
        resource: str,
        *,
        method: str = "GET",
        resource_for_monitoring: str | None = None,
        params: typedefs.Query = None,
        headers: typedefs.LooseHeaders | None = None,
        data: t.Any = None,
        json: t.Any = None,
        request_settings: dict | None = None,
        session: ClientSession | None = None,
    ) -> t.Any:
        resource_for_monitoring = resource_for_monitoring or resource
        url = self.api_root
        if resource:
            url = f"{self.api_root}/{resource}"
        headers = self.headers | (headers or {})
        request_settings = self.request_settings | (request_settings or {})

        async with session or self.session or self.Session() as sess:
            logger.log(self.log_level, "Call endpoint: %s %s", method, url)

            if self.logging_extra_data:
                if headers:
                    logger.debug("Headers: %s", headers)
                if params:
                    logger.debug("Params: %s", params)
                if data:
                    logger.debug("Data: %s", data)
                if json:
                    logger.debug("Json: %s", json)

            start_time = time.perf_counter()

            try:
                async with sess.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    json=json,
                    headers=headers,
                    **request_settings,
                ) as response:
                    duration = time.perf_counter() - start_time
                    logger.debug("End call endpoint: %s %s, duration %s ", method, url, duration)

                    if is_build_metrics():
                        request_headers = getattr(response.request_info, "headers", {}) or {}
                        response_headers = response.headers or {}
                        request_size = int(
                            request_headers.get("content-length", request_headers.get("Content-Length", 0)),
                        )
                        response_size = int(
                            response_headers.get("content-length", response_headers.get("Content-Length", 0)),
                        )
                        http_tracking(
                            app_type=self.name_for_monitoring,
                            resource=resource_for_monitoring,
                            method=str(method).upper(),
                            response_size=response_size,
                            status_code=response.status,
                            duration=duration,
                            request_size=request_size,
                        )

                    return await self.process_response(response)

            except AiohttpClientError as exc:
                duration = time.perf_counter() - start_time
                logger.error("Connection error: %s %s - %s", method, url, exc)

                if is_build_metrics():
                    http_tracking(
                        app_type=self.name_for_monitoring,
                        resource=resource_for_monitoring,
                        method=str(method).upper(),
                        response_size=0,
                        status_code=0,
                        duration=duration,
                        request_size=0,
                    )

                raise self.ConnectionError(url=url, method=method, original_error=exc) from exc

            except TimeoutError as exc:
                duration = time.perf_counter() - start_time
                logger.error("Timeout error: %s %s - %s", method, url, exc)

                if is_build_metrics():
                    http_tracking(
                        app_type=self.name_for_monitoring,
                        resource=resource_for_monitoring,
                        method=str(method).upper(),
                        response_size=0,
                        status_code=0,
                        duration=duration,
                        request_size=0,
                    )

                raise self.ConnectionError(url=url, method=method, original_error=exc) from exc

    async def response_to_native(self, response: ClientResponse) -> t.Any:
        try:
            return await response.json(loads=orjson.loads, content_type=None)
        except ValueError:
            return await response.text()

    async def error_handling(self, response: ClientResponse, response_data: t.Any) -> None:
        if 200 <= response.status < 300:
            return

        if 400 <= response.status < 500:
            raise self.ClientError(
                response=response,
                response_data=response_data,
                url=response.url,
                status_code=response.status,
            )

        if response.status >= 500:
            raise self.ServerError(
                response=response,
                response_data=response_data,
                url=response.url,
                status_code=response.status,
            )

        raise self.ApiError(response=response, response_data=response_data)

    async def process_response(self, response: ClientResponse) -> t.Any:
        response_data = await self.response_to_native(response)
        if self.logging_extra_data:
            logger.debug("Response data: %s", response_data)
        await self.error_handling(response, response_data)
        return response_data


class SyncApi:
    ApiError = ExternalApiError
    ServerError = ServerError
    ClientError = ClientError
    ConnectionError = ExternalHTTPConnectionError
    ClientSession = httpx.Client
    name_for_monitoring: str

    def __init__(
        self,
        api_root: str,
        *,
        name_for_monitoring: str,
        headers: dict | None = None,
        request_settings: dict | None = None,
        log_level: int | str = logging.INFO,
        logging_extra_data: bool = False,
    ):
        self.name_for_monitoring = name_for_monitoring
        self.api_root = api_root
        self.request_settings = request_settings or {}
        self.headers = headers or {}
        self.logging_extra_data = logging_extra_data
        self.log_level = log_level
        if isinstance(self.log_level, str):
            self.log_level = logging.getLevelNamesMapping()[self.log_level.upper()]
        self.session = None

    @contextmanager
    def Session(self, **session_settings):  # noqa: N802
        if self.session:
            yield self.session
        else:
            try:
                with self.ClientSession(**session_settings) as session:
                    self.session = session
                    yield session
            finally:
                self.session = None

    def call_endpoint(
        self,
        resource: str,
        *,
        method: str = "GET",
        resource_for_monitoring: str | None = None,
        params: dict | None = None,
        headers: dict | None = None,
        data: t.Any = None,
        json: t.Any = None,
        request_settings: dict | None = None,
        session: httpx.Client | None = None,
    ) -> t.Any:
        resource_for_monitoring = resource_for_monitoring or resource
        url = self.api_root
        if resource:
            url = f"{self.api_root}/{resource}"

        headers = self.headers | (headers or {})
        request_settings = self.request_settings | (request_settings or {})

        with session or self.session or self.Session() as sess:
            logger.log(self.log_level, "Call endpoint: %s %s", method, url)

            if self.logging_extra_data:
                if headers:
                    logger.debug("Headers: %s", headers)
                if params:
                    logger.debug("Params: %s", params)
                if data:
                    logger.debug("Data: %s", data)
                if json:
                    logger.debug("Json: %s", json)

            start_time = time.perf_counter()

            try:
                response = sess.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    json=json,
                    headers=headers,
                    **request_settings,
                )

                logger.debug("End call endpoint: %s %s, duration %s ", method, url, response.elapsed.total_seconds())

                if is_build_metrics():
                    http_tracking(
                        app_type=self.name_for_monitoring,
                        resource=resource_for_monitoring,
                        method=str(method).upper(),
                        response_size=int(response.headers.get("content-length", 0)),
                        status_code=response.status_code,
                        duration=response.elapsed.total_seconds(),
                        request_size=int(response.request.headers.get("content-length", 0)),
                    )

                return self.process_response(response)

            except httpx.ConnectError as exc:
                duration = time.perf_counter() - start_time
                logger.error("Connection error: %s %s - %s", method, url, exc)

                if is_build_metrics():
                    http_tracking(
                        app_type=self.name_for_monitoring,
                        resource=resource_for_monitoring,
                        method=str(method).upper(),
                        response_size=0,
                        status_code=0,
                        duration=duration,
                        request_size=0,
                    )

                raise self.ConnectionError(url=url, method=method, original_error=exc) from exc

            except httpx.TimeoutException as exc:
                duration = time.perf_counter() - start_time
                logger.error("Timeout error: %s %s - %s", method, url, exc)

                if is_build_metrics():
                    http_tracking(
                        app_type=self.name_for_monitoring,
                        resource=resource_for_monitoring,
                        method=str(method).upper(),
                        response_size=0,
                        status_code=0,
                        duration=duration,
                        request_size=0,
                    )

                raise self.ConnectionError(url=url, method=method, original_error=exc) from exc

            except httpx.HTTPStatusError as exc:
                duration = time.perf_counter() - start_time
                logger.error("HTTP status error: %s %s - %s", method, url, exc)

                if is_build_metrics():
                    http_tracking(
                        app_type=self.name_for_monitoring,
                        resource=resource_for_monitoring,
                        method=str(method).upper(),
                        response_size=0,
                        status_code=exc.response.status_code if exc.response else 0,
                        duration=duration,
                        request_size=0,
                    )

                raise self.ConnectionError(url=url, method=method, original_error=exc) from exc

    def response_to_native(self, response: httpx.Response) -> t.Any:
        try:
            return orjson.loads(response.content)
        except ValueError:
            return response.text

    def error_handling(self, response: httpx.Response, response_data: t.Any) -> None:
        if 200 <= response.status_code < 300:
            return

        if 400 <= response.status_code < 500:
            raise self.ClientError(
                response=response,
                response_data=response_data,
                url=response.url,
                status_code=response.status_code,
            )

        if response.status_code >= 500:
            raise self.ServerError(
                response=response,
                response_data=response_data,
                url=response.url,
                status_code=response.status_code,
            )

        raise self.ApiError(response=response, response_data=response_data)

    def process_response(self, response: httpx.Response) -> t.Any:
        response_data = self.response_to_native(response)
        if self.logging_extra_data:
            logger.debug("Response data: %s", response_data)
        self.error_handling(response, response_data)
        return response_data


class IClient(t.Protocol):
    """
    import project.exceptions

    class MyApiError(project.exceptions.ApiError):
        pass

    class MyServerError(project.exceptions.ServerError):
        pass

    class MyClientError(project.exceptions.ClientError):
        pass

    class MyConnectionError(project.exceptions.ConnectionError):
        pass

    class MyClient(IClient):
        ApiError = MyApiError
        ServerError = MyServerError
        ClientError = MyClientError
        ConnectionError = MyConnectionError

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
            self.api = self.Api(self.api_root, headers=headers, name_for_monitoring="my_api")

        async def my_endpoint():
            return await self.api.call_endpoint("resource_name", method="POST")

    client = MyClient("token")
    await client.my_endpoint()

    # with session
    async with client.api.Session():
        await client.my_endpoint()
    """

    ApiError: type[Exception]
    ServerError: type[Exception]
    ClientError: type[Exception]
    ConnectionError: type[Exception]

    Api: t.ClassVar[type[AsyncApi | SyncApi]]
    api_root: str
    api: AsyncApi | SyncApi
