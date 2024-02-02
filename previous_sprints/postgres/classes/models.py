from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID


@dataclass
class DefaultTable(object):
    """Базовый класс для таблиц."""

    id: UUID
    created: str
    modified: str


@dataclass
class DefaultTableMDF(object):
    """Базовый класс для таблиц."""

    id: UUID
    created: str


@dataclass
class Filmwork(DefaultTable):
    """Класс кинопроизведений."""

    title: str
    type: str
    description: str
    creation_date: str
    rating: float
    _index: ClassVar[str] = 'film_work'


@dataclass
class Person(DefaultTable):
    """Класс персон."""

    full_name: str
    _index: ClassVar[str] = 'person'


@dataclass
class Genre(DefaultTable):
    """Класс жанров."""

    name: str
    description: str
    _index: ClassVar[str] = 'genre'


@dataclass
class GenreFilmwork(DefaultTableMDF):
    """Класс жанров у кинопроизведений."""

    genre_id: str
    film_work_id: str
    _index: ClassVar[str] = 'genre_film_work'


@dataclass
class PersonFilmwork(DefaultTableMDF):
    """Класс персон у кинопроизведений."""

    person_id: str
    film_work_id: str
    role: str
    _index: ClassVar[str] = 'person_film_work'
