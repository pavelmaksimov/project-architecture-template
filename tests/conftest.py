import asyncio
import os
import pathlib

import pytest_asyncio
import responses as mock_responses
import pytest
from aioresponses import aioresponses
from starlette.testclient import TestClient

import project.domains.base.models
from project.infrastructure.adapters import database
from project.infrastructure.adapters import adatabase
from project.infrastructure.adapters import keycloak
from project.logger import setup_logging
from project.infrastructure.api import app
from project.settings import Settings
from project.utils.log import logging_disabled

default_test_settings = {
    "ENV": "TEST",
    "ACCESS_TOKEN": "token",
    "SQLALCHEMY_DATABASE_DSN": os.environ.get(
        "SQLALCHEMY_DATABASE_DSN", "postgresql+psycopg2://postgres:postgres@localhost:15432/test"
    ),
}


@pytest.fixture(scope="session")
def settings():
    yield Settings


@pytest.fixture(autouse=True, scope="session")
def setup(settings):
    setup_logging("DEV")

    os.environ.update(**default_test_settings)

    with settings.local(**default_test_settings):
        yield


@pytest.fixture(scope="session")
def init_database(setup):
    engine = database.engine_factory()

    with logging_disabled():
        project.domains.base.models.public_schema.create_all(bind=engine, checkfirst=True)

    engine.dispose()


@pytest.fixture(scope="function")
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


@pytest_asyncio.fixture(scope="function")
async def asession(init_database):
    async with adatabase.asession() as asession:
        async with asession.begin() as t:
            async with asession.begin_nested():
                yield asession
                # For the database to be clean, in the end the created data roll back.
            await t.rollback()


@pytest.fixture(scope="function")
def api_client(settings, session):
    yield TestClient(app, headers={"Access-Token": settings().ACCESS_TOKEN})


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


@pytest.fixture(scope="function")
def responses(mock_niquests):
    """Fixture for mocking asynchronous requests."""
    with mock_responses.RequestsMock() as mock:
        yield mock


@pytest.fixture(scope="function")
def aresponses():
    """Fixture for mocking asynchronous requests."""
    with aioresponses() as mock:
        yield mock


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def mock_keycloak(responses):
    responses.add(
        responses.POST,
        "http://keycloak.example.com/auth",
        json={"access_token": "test_token"},
        status=200,
    )


@pytest.fixture(scope="function")
def mock_async_keycloak(aresponses):
    aresponses.add(
        "http://keycloak.example.com/auth",
        method="POST",
        payload={"access_token": "test_token"},
        status=200,
    )


@pytest.fixture(scope="function")
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
