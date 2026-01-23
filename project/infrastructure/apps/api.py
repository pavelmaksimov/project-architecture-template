import time
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI, Depends, Header, status
from fastapi.exception_handlers import request_validation_exception_handler, http_exception_handler
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import ORJSONResponse
from llm_common.prometheus import fastapi_tracking_middleware, fastapi_endpoint_for_prometheus
from starlette.requests import Request

from project import exceptions
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
    message = f"Unexpected Error: {exc}"
    logger.exception(message)
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    message = f"{request.method} {request.url} {exc.status_code}"
    if exc.detail:
        message = f"{message} ({exc.detail})"

    if Settings().is_local():
        message = f"{message} headers={request.headers}"

    logger.error(message)

    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    message = f"{request.method} {request.url} {status.HTTP_422_UNPROCESSABLE_ENTITY} ({exc.errors()})"
    logger.error(message)
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(exceptions.NotFoundError)
async def not_found_error_handler(request: Request, exc: exceptions.NotFoundError):
    message = f"{request.method} {request.url} {status.HTTP_404_NOT_FOUND} ({exc})"
    logger.error(message)
    return ORJSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(exceptions.AuthError)
async def auth_error_handler(request: Request, exc: exceptions.NotFoundError):
    message = f"{request.method} {request.url} {status.HTTP_401_UNAUTHORIZED} ({exc})"
    logger.error(message)
    return ORJSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


@app.exception_handler(exceptions.ApiError)
async def integration_error_handler(request: Request, exc: exceptions.NotFoundError):
    message = f"{request.method} {request.url} {status.HTTP_500_INTERNAL_SERVER_ERROR} ({exc})"
    logger.error(message)
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


@app.middleware("http")
async def process_time(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = round(time.perf_counter() - start_time, 3)
    response.headers["X-Process-Time"] = str(process_time)
    logger.info("%s %s %s %s", request.method, request.url, response.status_code, process_time)

    return response


@app.get("/health", response_class=ORJSONResponse)
async def health_check():
    return health_response
