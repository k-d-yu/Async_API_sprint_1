from typing import ClassVar

from models.base import BaseMixin


class GenreResponseShort(BaseMixin):

    name: str
    index: ClassVar[str] = 'genres'


class GenreResponse(GenreResponseShort):

    description: str | None = None


class GenresResponseModel(BaseMixin):
    name: str
