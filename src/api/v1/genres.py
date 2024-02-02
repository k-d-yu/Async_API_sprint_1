from http import HTTPStatus
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate

from core.paginate import JSONAPIPage
from db.elastic import get_elastic
from db.redis import get_redis
from models.genres import GenreResponse, GenreResponseShort
from services.genres import GenreSearch

router = APIRouter()


async def get_genres_search(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreSearch:
    return GenreSearch(redis=redis, elastic=elastic, type_of_response=GenreResponse)


@router.get('/{genre_uuid}', response_model=GenreResponse, summary='Поиск жанра по ID',
            description='Поиск жанра по ID', response_description='Название и описание жанра',)
async def genre_get_api(
    genre_uuid: UUID,
    genres_search: GenreSearch = Depends(get_genres_search),
) -> GenreResponse:
    genre = await genres_search.get_doc_by_id(doc_id=genre_uuid)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='жанр не найден')
    return genre


@router.get('/', response_model=Page[GenreResponseShort], summary='Список жанров',
            description='Список жанров', response_description='Название жанра',)
async def genres_get_list_api(
    genres_search: GenreSearch = Depends(get_genres_search),
) -> JSONAPIPage[GenreResponseShort]:

    genres = await genres_search.search_list_of_docs()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='жанры не найдены')
    return paginate(sequence=genres, length_function=genres_search.count_docs)
