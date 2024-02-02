from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis

from core.config import settings
from models.film import FilmsElasticModel


class ServiceMixin:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str):
        self.redis = redis
        self.elastic = elastic
        self.total_count: int = 0
        self.index = index

    async def get_total_count(self) -> int:
        return self.total_count

    async def set_total_count(self, value: int):
        self.total_count = value

    async def search_in_elastic(self, body: dict, _source=None, sort=None, _index=None) -> dict:
        if not _index:
            _index = self.index
        try:
            return await self.elastic.search(index=_index, _source=_source, body=body, sort=sort)
        except NotFoundError:
            return None

    async def get_by_id(self, film_id: str):
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> FilmsElasticModel:
        try:
            doc = await self.elastic.get(index=self.index, id=film_id)
            return FilmsElasticModel(**doc["_source"])
        except NotFoundError:
            return None

    async def _film_from_cache(self, film_id: str) -> FilmsElasticModel:
        data = await self.redis.get(film_id)
        if not data:
            return None
        film = FilmsElasticModel.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: FilmsElasticModel):
        await self.redis.set(film.id, film.json(), settings.cache_lifetime)
