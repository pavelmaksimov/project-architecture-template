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


class ExternalApiError(AppError):
    def __init__(self, response, response_data):
        self.response = response
        self.response_data = response_data

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.response_data}"


class ServerError(ExternalApiError):
    def __init__(self, response, response_data, url, status_code):
        super().__init__(response, response_data)
        self.url = url
        self.status_code = status_code

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.status_code} ({self.response_data})"

    def __str__(self):
        return f"{self.response.method} {self.url} {self.status_code} ({self.response_data})"


class ClientError(ExternalApiError):
    def __init__(self, response, response_data, url, status_code):
        super().__init__(response, response_data)
        self.url = url
        self.status_code = status_code

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.status_code} ({self.response_data})"

    def __str__(self):
        return f"{self.response.method} {self.url} {self.status_code} ({self.response_data})"


class ExternalHTTPConnectionError(AppError):
    def __init__(self, url: str, method: str, original_error: Exception):
        self.url = url
        self.method = method
        self.original_error = original_error

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.method} {self.url} ({self.original_error})"
