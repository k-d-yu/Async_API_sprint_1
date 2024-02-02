from typing import Type, Union

from models.genres import GenreResponse
from models.persons import PersonDetailResponse, PersonResponse
from models.film import FilmResponse, FilmRoles

SCHEME = Union[
    Type[GenreResponse],
    Type[PersonResponse],
    Type[PersonDetailResponse],
    Type[FilmResponse],
    Type[FilmRoles],
]


def matching_keys(dicts, search_string: str):
    return [item for item in dicts if item.id == search_string]
