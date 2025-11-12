from pydantic import BaseModel


class BaseResponse[T](BaseModel):
    data: T
