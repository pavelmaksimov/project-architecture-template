import time
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI, Depends, Header, status
from fastapi.exception_handlers import request_validation_exception_handler, http_exception_handler
from fastapi.exceptions import RequestValidationError, StarletteHTTPException, HTTPException
from fastapi.responses import ORJSONResponse
from llm_common.prometheus import fastapi_tracking_middleware, fastapi_endpoint_for_prometheus
from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from project.components.chat.endpoints import router as chat_router
from project.logger import setup_logging
from project.settings import Settings, API_ROOT_PATH

logger = getLogger(__name__)

health_response = {"status": "ok"}


def auth_by_token(auth_token: str = Header(alias="Api-Token")):
    if Settings().is_local():
        return auth_token

    if auth_token != Settings().API_TOKEN.get_secret_value():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    return auth_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    logger.info("Connecting to database")

    yield


app = FastAPI(root_path=API_ROOT_PATH, lifespan=lifespan, dependencies=[Depends(auth_by_token)])
app.include_router(chat_router)

app.middleware("http")(fastapi_tracking_middleware)

app.get("/prometheus")(fastapi_endpoint_for_prometheus)


@app.exception_handler(Exception)
async def custom_exception_handler(request, exc: Exception):
    logger.exception("Unexpected Error: %s", str(exc))
    return exc


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc: StarletteHTTPException):
    logger.error(
        "%s %s, detail=%s, method=%s, url=%s, headers=%s",
        repr(exc.status_code),
        exc.__class__.__name__,
        repr(exc.detail),
        request.method,
        request.url,
        request.headers,
    )
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        "%s %s detail=%s method=%s url=%s headers=%s",
        HTTP_422_UNPROCESSABLE_ENTITY,
        exc.__class__.__name__,
        exc.errors(),
        request.method,
        request.url,
        request.headers,
    )
    return await request_validation_exception_handler(request, exc)


@app.middleware("http")
async def process_time(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = round(time.perf_counter() - start_time, 3)
    response.headers["X-Process-Time"] = str(process_time)
    logger.info("Response: %s %s %s", request.method, request.url, process_time)

    return response


@app.get("/health", response_class=ORJSONResponse)
async def health_check():
    return health_response
