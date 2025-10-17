class InfrastructureError(Exception):
    pass


class ApiError(InfrastructureError):
    def __init__(self, name, response):
        self.name = name
        self.response = response

    def __str__(self):
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

    def __str__(self):
        return f"{self.__class__.__name__}: {self.code} {self.message}{f' - {self.detail}' if self.detail else ''}"
