## API Best practices
uvicorn запускается с циклом uvloop
```bash
uvicorn project.presentation.api:app -host 0.0.0.0 --loop uvloop
```

Эндпоинты должны располагаться в `project.components.{name}.endpoints`.

### Формат ответов ресурсов API
Лучше возвращать в виде словаря.
Тогда при необходимости добавление новых данных в ответе ручки, нужно будет добавить только новое поле.
Используйте готовую схему для этого `project.components.base.schemas.BaseResponse`.
Если указать в аргументе response_model, в swagger появится документация по выводу.
Но в случае тяжелых данных это может быть затратно по времени,
потому что данные буду валидироваться через `pydantic`, это замедляет 2.5 раза по сравнению с обычным dict/dataclass.

```python
from project.components.base.schemas import BaseResponse


@app.get("/my", response_model=BaseResponse[list[int]])
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

### Ошибки HTTP
Не нужно тащить `fastapi.exceptions.HTTPException` в бизнес-логику, они должны оставаться в модулях `endpoints.py`.
