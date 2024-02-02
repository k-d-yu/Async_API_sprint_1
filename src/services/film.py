from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from services.mixin_for_film import ServiceMixin
from services.redis_service import RedisMixin

from models.film import FilmsElasticModel, FilmsResponseModel
from services.film_search_elastic import get_hits, get_params_films_to_elastic
from services.pagination import get_by_pagination
from models.persons import FilmPersonResponse
from core.misc import matching_keys, SCHEME


from core.base_search import BaseSearch


class FilmSearch(BaseSearch):

    def make_roles_list(self, films: list[SCHEME], person: dict):

        res = []

        for film in films:
            current = FilmPersonResponse(id=film.id)
            if matching_keys(film.actors, person['id']):
                current.roles.append('actor')
            if matching_keys(film.writers, person['id']):
                current.roles.append('writer')
            if matching_keys(film.directors, person['id']):
                current.roles.append('director')
            res.append(current)

        return res


class FilmService(ServiceMixin, RedisMixin):
    async def get_all_films(
            self,
            page: int,
            page_size: int,
            sorting: str = None,
            query: str = None,
            genre: str = None,
    ) -> dict:
        _source: tuple = ("id", "title", "imdb_rating", "genre")

        body: dict = get_params_films_to_elastic(page_size=page_size, page=page, genre=genre, query=query)
        redis_conditions: dict = {'page_size': page_size, 'page': page, 'sorting': sorting, 'query': query,
                                  'genre': genre, 'index': None,
                                  }
        try:
            redis_response = await self.get_from_redis(
                conditions=redis_conditions
            )
            if redis_response:
                films: list[dict] = redis_response.docs
                total: int = int(redis_response.total)
            else:
                docs: dict = await self.search_in_elastic(
                    body=body, _source=_source, sort=sorting
                )
                if not docs:
                    return None

                hits = get_hits(docs, FilmsElasticModel)
                total: int = int(docs.get("hits").get("total").get("value", 0))
                films: list[FilmsResponseModel] = [FilmsResponseModel(id=row.id, title=row.title,
                                                                      imdb_rating=row.imdb_rating) for row in hits]
                await self.put_to_redis(
                    conditions=redis_conditions,
                    docs=films,
                    total=total
                )

            await self.set_total_count(value=total)
            return get_by_pagination(
                name="films",
                db_objects=films,
                total=total,
                page=page,
                page_size=page_size,
            )
        except NotFoundError:
            return None


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis=redis, elastic=elastic, index="movies")
