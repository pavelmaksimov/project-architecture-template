## API Best practices
uvicorn запускается с циклом uvloop
```bash
uvicorn project.presentation.api:app -host 0.0.0.0 --loop uvloop
```

Эндпоинты должны располагаться в `project.components.{name}.endpoints`.

### Формат ответов ресурсов API
Лучше возвращать в виде словаря.
Тогда при необходимости добавление новых данных в ответе ручки, нужно будет добавить только новое поле.
Используйте готовую схему для этого `project.components.base.schemas.ApiResponse`.
Если указать в аргументе response_model, в swagger появится документация по выводу.
Но в случае тяжелых данных это может быть затратно по времени,
потому что данные буду валидироваться через `pydantic`, это замедляет 2.5 раза по сравнению с обычным dict/dataclass.

```python
from project.components.base.schemas import ApiResponseSchema


@app.get("/my", response_model=ApiResponseSchema[list[int]])
async def my_resource():
    return {"data": [1, 2]}
```

### Аутентификация по токену в API
Проверка уже зашита в эндпоинты.
```python
def auth_by_token(auth_token: str = Header(alias="Api-Token")):
    if auth_token != Settings().API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    return auth_token

app = FastAPI(..., dependencies=[Depends(auth_by_token)])
```

### Быстрая сериализация в JSON
 `ORJSONResponse` использует пакет `orjson` написанный на `RUST`, очень быстрый.
Можно указывать в самой ручке через аргумент `response_class`.

```python
from fastapi.responses import ORJSONResponse

@app.get("/health", response_class=ORJSONResponse)
async def health_check():
    return {}
```

### Версионирование
- Версионирование через URL путь `/user/v1/list`
- Изменение ручек делаем через добавление новой ручки с новой версией, а предыдущую помечаем `deprecated`.
```
@app.get("/user/v1/list", deprecated=True)
```


## Обработка исключений в FastAPI

### Правильный подход к обработке исключений

Поток обработки ошибок: Бизнес-логика → raise Exception → FastAPI Exception Handler → HTTP Response

**В бизнес-логике** поднимать обычные исключения (наследники `AppError`):

```python
# В use cases, services, repositories
def process_user(user_id: int):
    user = user_repo.get(user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    return user
```

**В FastAPI эндпоинтах** использовать обработчики исключений FastAPI для преобразования бизнес-исключений в HTTP ответы:

```python
app = FastAPI(...)

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


@app.exception_handler(exceptions.ExternalApiError)
async def integration_error_handler(request: Request, exc: exceptions.NotFoundError):
    message = f"{request.method} {request.url} {status.HTTP_500_INTERNAL_SERVER_ERROR} ({exc})"
    logger.error(message)
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )
```

### Почему так правильно?

1. **Разделение ответственностей**: Бизнес-логика не знает о HTTP, фреймворк обрабатывает HTTP аспекты
2. **Переиспользование**: Одна бизнес-логика может использоваться в разных контекстах (API, CLI, тесты)
3. **Тестируемость**: Легче тестировать бизнес-логику без HTTP зависимостей
4. **Читаемость**: Код бизнес-логики фокусируется на логике, а не на HTTP деталях

### Антипаттерны

❌ **Не использовать HTTPException в бизнес-логике:**
```python
# ПЛОХО: бизнес-логика зависит от FastAPI
def process_user(user_id: int):
    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")  # ❌
    return user
```

❌ **Не подавлять исключения в эндпоинтах:**
```python
# ПЛОХО: скрывает ошибки
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        user = await user_service.get_user(user_id)
        return user
    except Exception as e:
        return {"error": "Something went wrong"}  # ❌
```
