import pathlib

import pytest
import pytest_asyncio
from aioresponses import aioresponses
from starlette.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer, AsyncRedisContainer

import project.components.base.models
from project.infrastructure.adapters import adatabase
from project.infrastructure.adapters import database
from project.infrastructure.adapters import keycloak
from project.infrastructure.apps.api import app
from project.logger import setup_logging
from project.settings import Settings
from project.libs.log import logging_disabled


@pytest.fixture(autouse=True, scope="session")
def setup():
    with Settings.local(
        ENV="TEST",
        API_TOKEN="token",
        LLM_MODEL="LLM_MODEL",
        LLM_API_KEY="LLM_API_KEY",
    ):
        setup_logging()

        yield


@pytest.fixture(scope="session")
def init_database(setup):
    with PostgresContainer("postgres:17.2") as postgres:
        with Settings.local(
            **{
                **Settings().model_dump(exclude_unset=True),
                "SQLALCHEMY_DATABASE_DSN": postgres.get_connection_url(),
            },
        ):
            engine = database.engine_factory()

            try:
                with logging_disabled():
                    project.components.base.models.public_schema.create_all(bind=engine, checkfirst=True)

                yield engine

            finally:
                engine.dispose()


@pytest.fixture(scope="session")
def init_redis(setup):
    with RedisContainer("redis") as redis_container:
        client = redis_container.get_client()
        connection_kwargs = client.get_connection_kwargs()
        with Settings.local(
            **{
                **Settings().model_dump(exclude_unset=True),
                "REDIS_HOST": connection_kwargs["host"],
                "REDIS_PORT": connection_kwargs["port"],
                "REDIS_DB": str(connection_kwargs["db"]),
            },
        ):
            yield client


@pytest.fixture
def redis(init_redis):
    yield init_redis
    init_redis.reset()
    init_redis.flushdb()


@pytest_asyncio.fixture(scope="session")
async def async_init_redis(setup):
    with AsyncRedisContainer("redis") as redis_container:
        client = await redis_container.get_async_client()
        connection_kwargs = client.get_connection_kwargs()
        with Settings.local(
            **{
                **Settings().model_dump(exclude_unset=True),
                "REDIS_HOST": connection_kwargs["host"],
                "REDIS_PORT": connection_kwargs["port"],
                "REDIS_DB": str(connection_kwargs["db"]),
            },
        ):
            yield client


@pytest_asyncio.fixture
async def async_redis(async_init_redis):
    yield async_init_redis
    await async_init_redis.reset()
    await async_init_redis.flushdb()


@pytest.fixture
def session(init_database):
    with database.Session() as session:
        with session.begin() as t:
            with session.begin_nested():
                yield session
                # For the database to be clean, in the end the created data roll back.
            t.rollback()

    database.engine_factory.cache_clear()
    database.scoped_session_factory.cache_clear()


@pytest_asyncio.fixture
async def asession(init_database):
    async with adatabase.asession() as asession:
        async with asession.begin() as t:
            async with asession.begin_nested():
                yield asession
                # For the database to be clean, in the end the created data roll back.
            await t.rollback()

    adatabase.aengine_factory.cache_clear()
    adatabase.async_sessionmaker_factory.cache_clear()


@pytest.fixture
def api_client(session):
    return TestClient(app, headers={"Api-Token": Settings().API_TOKEN.get_secret_value()})


@pytest.fixture
def httpx_responses():
    """Fixture for mocking httpx requests using respx with a 'responses'-like API."""
    import httpx
    import respx

    class _ResponsesWrapper:
        def __init__(self, router: respx.Router):
            self._router = router

        def add(self, method, url, json=None, status_code=200, headers=None):
            # Register a route and set a mock response
            route = self._router.request(method, url)
            if json is not None:
                route.mock(return_value=httpx.Response(status_code, json=json, headers=headers))
            else:
                route.mock(return_value=httpx.Response(status_code, headers=headers))
            return route

    with respx.mock as router:
        yield _ResponsesWrapper(router)


@pytest.fixture
def aiohttp_responses():
    """Fixture for mocking asynchronous requests."""
    with aioresponses() as mock:
        yield mock


@pytest.fixture
def keycloak_client():
    with Settings.local(
        **Settings().model_dump(exclude_unset=True),
        KEYCLOAK_URL="http://keycloak.example.com/auth",
        KEYCLOAK_CLIENT_ID="KEYCLOAK_CLIENT_ID",
        KEYCLOAK_USERNAME="KEYCLOAK_USERNAME",
        KEYCLOAK_PASSWORD="KEYCLOAK_PASSWORD",
    ):
        yield keycloak.KeycloakSyncClient(
            keycloak_url=Settings().KEYCLOAK_URL,
            client_id=Settings().KEYCLOAK_CLIENT_ID,
            username=Settings().KEYCLOAK_USERNAME,
            password=Settings().KEYCLOAK_PASSWORD.get_secret_value(),
        )


@pytest.fixture
def mock_keycloak(httpx_responses):
    httpx_responses.add(
        "POST",
        "http://keycloak.example.com/auth",
        json={"access_token": "test_token"},
        status=200,
    )


@pytest.fixture
def mock_async_keycloak(aiohttp_responses):
    aiohttp_responses.add(
        "http://keycloak.example.com/auth",
        method="POST",
        payload={"access_token": "test_token"},
        status=200,
    )


@pytest.fixture
def keycloak_aclient():
    with Settings.local(
        **Settings().model_dump(exclude_unset=True),
        KEYCLOAK_URL="http://keycloak.example.com/auth",
        KEYCLOAK_CLIENT_ID="KEYCLOAK_CLIENT_ID",
        KEYCLOAK_USERNAME="KEYCLOAK_USERNAME",
        KEYCLOAK_PASSWORD="KEYCLOAK_PASSWORD",
    ):
        yield keycloak.KeycloakAsyncClient(
            keycloak_url=Settings().KEYCLOAK_URL,
            client_id=Settings().KEYCLOAK_CLIENT_ID,
            username=Settings().KEYCLOAK_USERNAME,
            password=Settings().KEYCLOAK_PASSWORD.get_secret_value(),
        )


@pytest.fixture(scope="session")
def project_dir():
    path = pathlib.Path().cwd()

    if test_dir := list(path.rglob("project")):
        return test_dir[0]

    while 1:
        if path.name != "tests":
            path = path.parent
        else:
            return path.parent / "project"
