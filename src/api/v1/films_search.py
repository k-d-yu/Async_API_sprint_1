import enum
from fastapi import Query


class FilmSortImdbRating(str, enum.Enum):
    ascending = 'imdb_rating'
    descending = 'imdb_rating:desc'


class FilmsQuerySearch:
    def __init__(
            self,
            sort_imdb_rating: FilmSortImdbRating | None = Query(
            FilmSortImdbRating.ascending,
                title='Сортировка по рейтингу',
                description='Сортирует по возрастанию и убыванию',
            ),
            genre_filter: str | None = Query(
                None,
                title='Фильтр жанров',
                description='Фильтрует фильмы по жанрам',
                alias='filter[genre]'
            ),
            query: str | None = Query(
                None,
                title='Запрос',
                description='Осуществляет поиск по названию фильма',
            ),

    ) -> None:
        self.sort = sort_imdb_rating,
        self.genre_filter = genre_filter
        self.query = query
