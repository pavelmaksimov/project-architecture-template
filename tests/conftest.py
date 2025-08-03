import asyncio
import pathlib

import pytest
import pytest_asyncio
import responses as mock_responses
from aioresponses import aioresponses
from starlette.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer, AsyncRedisContainer

import project.domains.base.models
from project.infrastructure.adapters import adatabase
from project.infrastructure.adapters import database
from project.infrastructure.adapters import keycloak
from project.infrastructure.api import app
from project.logger import setup_logging
from project.settings import Settings
from project.utils.log import logging_disabled


@pytest.fixture(scope="session")
def settings():
    return Settings


@pytest.fixture(autouse=True, scope="session")
def setup(settings):
    setup_logging("TEST")

    with settings.local(ENV="TEST", ACCESS_TOKEN="token"):
        yield


@pytest.fixture(scope="session")
def init_database(settings, setup):
    with PostgresContainer("postgres:17.2") as postgres:
        with settings.local(SQLALCHEMY_DATABASE_DSN=postgres.get_connection_url()):

            engine = database.engine_factory()

            try:
                with logging_disabled():
                    project.domains.base.models.public_schema.create_all(bind=engine, checkfirst=True)

                yield engine

            finally:
                engine.dispose()


@pytest.fixture(scope="session")
def init_redis(settings, setup):
    with RedisContainer("redis") as redis_container:
        client = redis_container.get_client()
        connection_kwargs = client.get_connection_kwargs()
        with settings.local(
            REDIS_HOST=connection_kwargs["host"],
            REDIS_PORT=connection_kwargs["port"],
            REDIS_DB=str(connection_kwargs["db"]),
        ):
            yield client


@pytest.fixture
def redis(init_redis):
    yield init_redis
    init_redis.reset()
    init_redis.flushdb()


@pytest_asyncio.fixture(scope="session")
async def async_init_redis(settings, setup):
    with AsyncRedisContainer("redis") as redis_container:
        client = await redis_container.get_async_client()
        connection_kwargs = client.get_connection_kwargs()
        with settings.local(
            REDIS_HOST=connection_kwargs["host"],
            REDIS_PORT=connection_kwargs["port"],
            REDIS_DB=str(connection_kwargs["db"]),
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


@pytest.fixture(scope="session")
def event_loop():
    """
    This corrects the problem with sessions from the database, you need to run all the tests in one event loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def asession(init_database):
    async with adatabase.asession() as asession:
        async with asession.begin() as t:
            async with asession.begin_nested():
                yield asession
                # For the database to be clean, in the end the created data roll back.
            await t.rollback()


@pytest.fixture
def api_client(settings, session):
    return TestClient(app, headers={"Access-Token": settings().ACCESS_TOKEN})


@pytest.fixture(scope="session")
def mock_niquests():
    """https://niquests.readthedocs.io/en/stable/community/extensions.html"""
    from sys import modules
    import niquests
    from niquests.packages import urllib3

    # responses is tied to Requests
    # and Niquests is entirely compatible with it.
    # we can fool it without effort.
    modules["requests"] = niquests
    modules["requests.adapters"] = niquests.adapters
    modules["requests.models"] = niquests.models
    modules["requests.exceptions"] = niquests.exceptions
    modules["requests.packages.urllib3"] = urllib3


@pytest.fixture
def responses(mock_niquests):
    """Fixture for mocking asynchronous requests."""
    with mock_responses.RequestsMock() as mock:
        yield mock


@pytest.fixture
def aresponses():
    """Fixture for mocking asynchronous requests."""
    with aioresponses() as mock:
        yield mock


@pytest.fixture
def keycloak_client(settings):
    with settings.local(
        KEYCLOAK_URL="http://keycloak.example.com/auth",
        KEYCLOAK_CLIENT_ID="KEYCLOAK_CLIENT_ID",
        KEYCLOAK_USERNAME="KEYCLOAK_USERNAME",
        KEYCLOAK_PASSWORD="KEYCLOAK_PASSWORD",
    ):
        yield keycloak.KeycloakSyncClient(
            keycloak_url=settings().KEYCLOAK_URL,
            client_id=settings().KEYCLOAK_CLIENT_ID,
            username=settings().KEYCLOAK_USERNAME,
            password=settings().KEYCLOAK_PASSWORD,
        )


@pytest.fixture
def mock_keycloak(responses):
    responses.add(
        responses.POST,
        "http://keycloak.example.com/auth",
        json={"access_token": "test_token"},
        status=200,
    )


@pytest.fixture
def mock_async_keycloak(aresponses):
    aresponses.add(
        "http://keycloak.example.com/auth",
        method="POST",
        payload={"access_token": "test_token"},
        status=200,
    )


@pytest.fixture
def keycloak_aclient(settings):
    with settings.local(
        KEYCLOAK_URL="http://keycloak.example.com/auth",
        KEYCLOAK_CLIENT_ID="KEYCLOAK_CLIENT_ID",
        KEYCLOAK_USERNAME="KEYCLOAK_USERNAME",
        KEYCLOAK_PASSWORD="KEYCLOAK_PASSWORD",
    ):
        yield keycloak.KeycloakAsyncClient(
            keycloak_url=settings().KEYCLOAK_URL,
            client_id=settings().KEYCLOAK_CLIENT_ID,
            username=settings().KEYCLOAK_USERNAME,
            password=settings().KEYCLOAK_PASSWORD,
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
