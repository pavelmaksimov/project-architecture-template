# Не создавайте глобальные объекты

глобальные объекты это топ антипаттерн, далующий программу крайне плохой (TODO: написать подробнее почему).

Вместо них создавайте объекты с ленивой инициализацией (в момент реального использования объекта)

Самый простой и частый вариант это создать фнукцию с кешом.
Там где используете клиент, вы вызываете эту функцию и получаете объект, это позволяет отложить инициализацию до 
момента реально использования.

```python
from functools import cache
from langchain_openai import ChatOpenAI
from project.settings import Settings

@cache
def client():
    return ChatOpenAI(
        api_key=Settings().LLM_API_KEY.get_secret_value(),
    )

async def llm_logic():
    result = await client().ainvoke()
```

Если в тестах нужно инициализировать объект с другими параметрами, тогда можете использовать
`LazyInit` из [structures.py](project/libs/structures.py), он предоставляют механизм ленивой инициализации и 
контекстный менеджер для инициализации объекта с другими параметрами.

Пример такого использования для класса [Settings](project/settings.py), который под капотом получает переменные 
окружения, а в тестах мы хотим заменять переменные окружения.

```python
# ✅ ПРАВИЛЬНО - объявление класса
class MyServiceClass:
    def __init__(self, param):
        self.param = param
        
    def do_something(self):
        return self.param

MyService = LazyInit(MyServiceClass, kwargs_func=lambda: {"param": Settings().PARAM})

# ❌ НЕПРАВИЛЬНО - инициализация в глобальной области
result = MyService().do_something()

# ❌ НЕПРАВИЛЬНО - сохранение экземпляра в глобальной области
my_service = MyService()  # ❌ ПЛОХО
my_service.do_something()

# ✅ ПРАВИЛЬНО - сохранение в атрибутах экземпляра допускается, потому что экземпляр создается лениво.
class MyClass:
    def __init__(self):
        self.adapter = GitLabAdapter()
        
# ✅ ПРАВИЛЬНО - Вызов внутри функции будет инициализироваться лениво
def myfunc():
    x = MyService().do_something()
```