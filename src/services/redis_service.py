import json
import hashlib
from redis.asyncio import Redis
from core.config import settings
from pydantic import BaseModel


class RedisResponse(BaseModel):
    docs: list[dict]
    total: int = None


class RedisMixin:
    def __init__(self, redis: Redis, index: str) -> None:
        self.redis = redis
        self.index = index

    async def get_from_redis(self, conditions: dict) -> RedisResponse:
        """
        Возвращает документы из Redis
        :param conditions: параметры запроса
        :return: документы и общее количество документов
        """
        key = self._get_key(conditions)
        results = await self.redis.get(key)
        if not results:
            return None
        return RedisResponse.parse_obj(json.loads(results))

    async def put_to_redis(self, conditions: dict, docs: list, total: int | None = None) -> None:
        """
        Сохраняет документы и количество документов в Redis
        :param conditions: условия
        :param docs: документы
        :param total: количество документов
        :return:
        """
        key = self._get_key(conditions)
        await self.redis.set(key,
                             RedisResponse(docs=docs, total=total).json(),
                             settings.cache_lifetime)

    def _get_key(self, conditions: dict) -> str:
        return (conditions['index'] if conditions['index'] else self.index) + hashlib.md5(
            json.dumps(conditions).encode()
        ).hexdigest()
