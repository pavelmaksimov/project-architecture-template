import typing as t
from datetime import timedelta

import orjson

from project.components.base.repositories import ORMModelRepository, CacheRepository
from project.components.user import models
from project.components.user.schemas import UserCacheSchema
from project.datatypes import UserIdT
from project.infrastructure.adapters.acache import redis_atransaction

if t.TYPE_CHECKING:
    from pydantic import BaseModel


class UserRepository(ORMModelRepository[models.UserModel]):
    _model = models.UserModel


class UserCacheRepository(CacheRepository):
    key_template = "user:{}"
    ttl = timedelta(days=7)

    @classmethod
    async def save(cls, user_id: UserIdT, data: "BaseModel"):
        async with redis_atransaction() as tr:
            content = orjson.dumps(data.model_dump(exclude_unset=True))
            tr.set(cls.key_template.format(user_id), content, ex=cls.ttl)

    @classmethod
    async def get(cls, user_id: UserIdT):
        content = await cls.client().get(cls.key_template.format(user_id))
        if content:
            data = orjson.loads(content)
            return UserCacheSchema(**data)

        return content

    @classmethod
    async def delete(cls, user_id: UserIdT):
        async with redis_atransaction() as tr:
            tr.delete(cls.key_template.format(user_id))
