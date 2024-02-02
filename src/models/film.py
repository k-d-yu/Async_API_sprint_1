from pydantic import BaseModel
from typing import ClassVar

from models.base import BaseMixin
from models.genres import GenresResponseModel
from models.persons import PersonsResponseModel


class FilmsElasticModel(BaseMixin):
    _index: ClassVar[str] = 'movies'
    title: str
    description: str | None = None
    imdb_rating: float
    genres: list[dict[str, str]] | None = None
    actors: list[dict[str, str]] | None = None
    writers: list[dict[str, str]] | None = None
    directors: list[dict[str, str]] | None = None


class FilmsResponseModel(BaseMixin):
    title: str
    imdb_rating: float


class FilmsDetailsResponseModel(FilmsResponseModel):
    description: str | None = None
    genres: list[GenresResponseModel] | None = None
    actors: list[PersonsResponseModel] | None = None
    writers: list[PersonsResponseModel] | None = None
    directors: list[PersonsResponseModel] | None = None


class FilmPagination(BaseModel):
    total: int
    page: int
    page_size: int
    next_page: int | None = None
    previous_page: int | None = None
    available_pages: int
    films: list[FilmsResponseModel] = None


class FilmResponse(BaseMixin):
    title: str
    imdb_rating: float
    index: ClassVar[str] = 'movies'


class FilmRoles(FilmResponse):
    actors: list[PersonsResponseModel] | None = None
    writers: list[PersonsResponseModel] | None = None
    directors: list[PersonsResponseModel] | None = None
