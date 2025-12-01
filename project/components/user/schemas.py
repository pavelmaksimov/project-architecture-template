import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class UserCacheSchema(BaseModel):
    user_id: int
