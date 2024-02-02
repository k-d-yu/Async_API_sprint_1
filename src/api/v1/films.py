from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Query

from api.v1.films_search import FilmsQuerySearch
from models.film import FilmsDetailsResponseModel, FilmPagination
from models.persons import PersonsResponseModel
from models.genres import GenresResponseModel
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get('/', response_model=FilmPagination, summary='Поиск кинопроизведений',
            description='Полнотекстовый поиск по кинопроизведениям', response_description='Название и рейтинг фильма', )
async def search_film_list(params: FilmsQuerySearch = Depends(),
                           film_service: FilmService = Depends(get_film_service),
                           page: int = Query(0, ge=0, description='Номер страницы'),
                           size: int = Query(10, ge=1, description='Размер страницы')) -> FilmPagination:
    films = await film_service.get_all_films(
        sorting=params.sort,
        page=page,
        page_size=size,
        query=params.query,
        genre=params.genre_filter
    )

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')

    return FilmPagination(**films)


@router.get('/{film_id}', response_model=FilmsDetailsResponseModel, summary='Поиск кинопроизведения по ID',
            description='Поиск кинопроизведения по ID', response_description='Полная информация о фильме', )
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) \
        -> FilmsDetailsResponseModel:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    genres_list: list[GenresResponseModel] = [GenresResponseModel(**genre) for genre in film.genres]
    actors_list: list[PersonsResponseModel] = [PersonsResponseModel(**actor) for actor in film.actors]
    writers_list: list[PersonsResponseModel] = [PersonsResponseModel(**writer) for writer in film.writers]
    directors_list: list[PersonsResponseModel] = [PersonsResponseModel(**director) for director in film.directors]
    return FilmsDetailsResponseModel(
        id=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=genres_list,
        actors=actors_list,
        writers=writers_list,
        directors=directors_list,
    )
