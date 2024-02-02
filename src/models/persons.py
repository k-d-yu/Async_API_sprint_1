from typing import ClassVar
from uuid import UUID

from models.base import BaseMixin


class PersonResponse(BaseMixin):

    full_name: str
    index: ClassVar[str] = 'persons'


class PersonsResponseModel(BaseMixin):

    name: str


class FilmPersonResponse(BaseMixin):

    roles: list[str] = []


class PersonDetailResponse(PersonResponse):

    films: list[FilmPersonResponse] | None = None


class PersonsDetailsResponseModel(PersonsResponseModel):
    role: str
    film_ids: list[UUID] | None = None
