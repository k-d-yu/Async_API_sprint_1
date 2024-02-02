from http import HTTPStatus
from uuid import UUID

from core.filters import films_by_person, persons_by_query, films_by_name
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, paginate

from db.elastic import get_elastic
from db.redis import get_redis
from core.paginate import JSONAPIPage
from models.persons import PersonResponse, PersonDetailResponse, FilmPersonResponse
from models.film import FilmRoles, FilmResponse
from services.persons import PersonSearch
from services.film import FilmSearch

router = APIRouter()


async def get_persons_search(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonSearch:
    return PersonSearch(redis=redis, elastic=elastic, type_of_response=PersonResponse)


async def get_films_search(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmSearch:
    return FilmSearch(redis=redis, elastic=elastic, type_of_response=FilmResponse)


async def get_films_search_details(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmSearch:
    return FilmSearch(redis=redis, elastic=elastic, type_of_response=FilmRoles)


@router.get('/', response_model=Page[PersonDetailResponse], summary='Поиск по имени/фамилии',
            description='Поиск по имени/фамилии', response_description='Имя, фамилия,фильмы и роль',)
async def person_list_api(
    full_name: str = Query(default='Angela'),
    persons_search: PersonSearch = Depends(get_persons_search),
    films_search: FilmSearch = Depends(get_films_search_details),
) -> JSONAPIPage[PersonDetailResponse]:
    films_with_name = await films_search.search_list_of_docs(films_by_name(full_name))
    length_films = lambda person_films: len(person_films)
    if not films_with_name:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='персоны не найдены')
    persons = {}
    for film in films_with_name:
        for actor in film.actors:
            if full_name in actor.name:
                if actor.id in persons:
                    if film.id in persons[actor.id]['films']:
                        persons[actor.id]['films'][film.id].append('actor')
                    else:
                        persons[actor.id]['films'][film.id] = ['actor']

                else:
                    persons[actor.id] = {
                        'id': actor.id,
                        'name': actor.name,
                        'films': {
                            film.id: ['actor'],
                        },
                    }
        for director in film.directors:
            if full_name in director.name:
                if director.id in persons:
                    if film.id in persons[director.id]['films']:
                        persons[director.id]['films'][film.id].append('director')
                    else:
                        persons[director.id]['films'][film.id] = ['director']

                else:
                    persons[director.id] = {
                        'id': director.id,
                        'name': director.name,
                        'films': {
                            film.id: ['director'],
                        },
                    }
        for writer in film.writers:
            if full_name in writer.name:
                if writer.id in persons:
                    if film.id in persons[writer.id]['films']:
                        persons[writer.id]['films'][film.id].append('writer')
                    else:
                        persons[writer.id]['films'][film.id] = ['writer']

                else:
                    persons[writer.id] = {
                        'id': writer.id,
                        'name': writer.name,
                        'films': {
                            film.id: ['writer'],
                        },
                    }
    res = [
        PersonDetailResponse(
            id=values['id'],
            full_name=values['name'],
            films=[
                FilmPersonResponse(
                    id=key,
                    roles=value,
                ) for key, value in values['films'].items()
            ],
        ) for person, values in persons.items()
    ]
    # TODO сократить преобразования чтобы снизить время работы сервиса
    return paginate(
        sequence=res,
        length_function=length_films,
    )


@router.get('/{person_uuid}', response_model=PersonDetailResponse, summary='Поиск персоны по ID',
            description='Поиск персоны по ID', response_description='Имя, фамилия и фильмы персоны',)
async def person_get_api(
    person_uuid: UUID,
    persons_search: PersonSearch = Depends(get_persons_search),
    films_search: FilmSearch = Depends(get_films_search_details),
) -> PersonDetailResponse:
    person = await persons_search.get_doc_by_id(doc_id=person_uuid)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='персона не найдена')
    person_films = films_search.make_roles_list(
        await films_search.search_list_of_docs(films_by_person(person.__dict__)),
        person.__dict__,
    )
    return PersonDetailResponse(
        id=person.id,
        full_name=person.full_name,
        films=person_films,
    )


@router.get(
    '/{person_uuid}/film',
    response_model=Page[FilmResponse],
    summary='Поиск персоны по ID и выдача всех его кинопроизведений',
    description='Поиск персоны по ID и выдача всех его кинопроизведений',
    response_description='Название кинопроизведения',
)
async def person_film_api(
    person_uuid: UUID,
    persons_search: PersonSearch = Depends(get_persons_search),
    films_search: FilmSearch = Depends(get_films_search),
) -> JSONAPIPage[FilmResponse]:
    person = await persons_search.get_doc_by_id(doc_id=person_uuid)
    person_films = await films_search.search_list_of_docs(films_by_person(person.__dict__))
    length_films = lambda person_films: len(person_films)
    if not person_films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='персона не найдена')
    return paginate(
        sequence=sorted(person_films, key=lambda d: d.imdb_rating, reverse=True),
        length_function=length_films,
    )
