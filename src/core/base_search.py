from http import HTTPStatus
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import HTTPException
from services.redis_service import RedisMixin

from core.misc import SCHEME
from core.config import settings


class BaseSearch(RedisMixin):

    def __init__(self, elastic: AsyncElasticsearch, redis: Redis, type_of_response: SCHEME):
        self.elastic = elastic
        self.redis = redis
        self.type_of_response = type_of_response

    def __post_init__(self):
        self.index = self.type_of_response.index

    def count_docs(self, list_of_docs) -> int:
        return len(list_of_docs)

    async def search_list_of_docs(self, query: dict | None = None):
        body = {'size': settings.max_window_size}
        if query:
            body['query'] = query['query']
        else:
            body['query'] = {'match_all': {}}
        redis_conditions: dict = {'query': query, 'index': self.type_of_response.index}
        try:
            redis_response = await self.get_from_redis(
                conditions=redis_conditions,
            )
            if redis_response:
                res: list[dict] = redis_response.docs
            else:
                data = await self.elastic.search(
                    index=self.type_of_response.index, body=body,
                )
                res = [document['_source'] for document in data['hits']['hits']]
        except NotFoundError:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        await self.put_to_redis(
            conditions=redis_conditions,
            docs=res,
        )
        return [self.type_of_response(**rec) for rec in res]
    
    async def get_doc_by_id(self, doc_id: str):
        entity = await self._get_from_cache(doc_id)
        if not entity:
            entity = await self.get_doc_from_es(doc_id)
            if not entity:
                return None
            await self._put_film_to_cache(entity)
        return entity

    async def get_doc_from_es(self, doc_id: UUID):
        try:
            data = await self.elastic.get(self.type_of_response.index, doc_id)
        except NotFoundError:
            return None
        return self.type_of_response(**data['_source'])

    async def _get_from_cache(self, entity_id: str):
        data = await self.redis.get(str(entity_id))
        if not data:
            return None
        film = self.type_of_response.parse_raw(data)
        return film

    async def _put_film_to_cache(self, entity: SCHEME):
        await self.redis.set(entity.id, entity.json(), settings.cache_lifetime)
