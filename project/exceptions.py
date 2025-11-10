import typing as t


def throw(exc: type[Exception], *args, **kwargs):
    raise exc(*args, **kwargs)


class AppError(Exception):
    pass


class AuthError(AppError):
    def __init__(self, user_id: int):
        self.user_id = user_id

    def __repr__(self):
        return f"AuthError: user_id={self.user_id}"

    def __str__(self):
        return f"Ошибка аутентификации: доступ для {self.user_id} отсутствует"


class NotFoundError(AppError, ValueError):
    def __init__(self, object_name: str, id: t.Any):
        super().__init__()
        self.object_name = object_name
        self.id = id

    def __repr__(self):
        return f"NotFoundError: {self.object_name}={self.id} not found"


class ApiError(AppError):
    def __init__(self, name, response):
        self.name = name
        self.response = response

    def __repr__(self):
        return (
            f"{self.__class__.__name__}: {self.name} {self.response.status} {self.response.reason} {self.response.text}"
        )


class ServerError(ApiError):
    def __init__(self, response, response_data):
        self.response = response
        self.response_data = response_data


class ClientError(ApiError):
    def __init__(self, response, code, message, detail):
        self.response = response
        self.code = code
        self.message = message
        self.detail = detail

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.code} {self.message}{f' - {self.detail}' if self.detail else ''}"
