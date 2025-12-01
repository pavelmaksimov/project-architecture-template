import pytest

from project.infrastructure.utils.base_client import AsyncApi
from project.exceptions import ApiError, ServerError, ClientError


@pytest.fixture
def api():
    return AsyncApi(api_root="http://example.com", headers={"Authorization": "Bearer token"}, name_for_monitoring="Api")


@pytest.mark.asyncio
async def test_call_endpoint_success(api, aiohttp_responses):
    aiohttp_responses.get("http://example.com/test", status=200, payload={"key": "value"})
    result = await api.call_endpoint("test")

    assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_response_to_native_text(api, aiohttp_responses):
    aiohttp_responses.get("http://example.com/test", status=200, body="text response")
    result = await api.call_endpoint("test")

    assert result == "text response"


@pytest.mark.asyncio
async def test_client_error(api, aiohttp_responses):
    aiohttp_responses.get("http://example.com/test", status=400, body="Error detail")

    with pytest.raises(ClientError) as exc_info:
        await api.call_endpoint("test")

    assert exc_info.value.code == 400
    assert exc_info.value.message == "Bad Request"
    assert exc_info.value.detail == "Error detail"


@pytest.mark.asyncio
async def test_server_error(api, aiohttp_responses):
    aiohttp_responses.get("http://example.com/test", status=500, body="Server error")

    with pytest.raises(ServerError) as exc_info:
        await api.call_endpoint("test")

    assert exc_info.value.response.status == 500
    assert exc_info.value.response_data == "Server error"


@pytest.mark.asyncio
async def test_headers_merge(api, aiohttp_responses):
    aiohttp_responses.get("http://example.com/test", status=200)

    await api.call_endpoint("test", headers={"X-Header": "value"})

    request = list(aiohttp_responses.requests.values())[0][0]

    assert request.kwargs["headers"] == {"Authorization": "Bearer token", "X-Header": "value"}


@pytest.mark.asyncio
async def test_successful_get_request(api, aiohttp_responses):
    test_data = {"result": "success"}
    aiohttp_responses.get("http://example.com/resource", status=200, payload=test_data)

    result = await api.call_endpoint("resource", method="GET")
    assert result == test_data


@pytest.mark.asyncio
async def test_unknown_status_error(api, aiohttp_responses):
    aiohttp_responses.get("http://example.com/test", status=304)

    with pytest.raises(ApiError) as exc_info:
        await api.call_endpoint("test")

    assert "304 Not Modified" in str(exc_info.value)


def test_exception_inheritance():
    assert issubclass(ClientError, ApiError)
    assert issubclass(ServerError, ApiError)
