from pydantic import BaseModel


class ApiResponseSchema[T](BaseModel):
    data: T
