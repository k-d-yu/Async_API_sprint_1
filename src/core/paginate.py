from math import ceil
from typing import Any, Generic, Sequence, TypeVar

from fastapi import Query
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from fastapi_pagination.types import GreaterEqualOne, GreaterEqualZero
from fastapi_pagination.utils import create_pydantic_model
from pydantic import BaseModel
from typing_extensions import Self

from core.config import settings

T = TypeVar('T')


class JSONAPIParams(BaseModel, AbstractParams):
    page_num: int = Query(default=settings.page_number, ge=0, description='номер страницы')
    size: int = Query(default=settings.page_size, ge=1, le=100, description='размер страницы')

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size,
            offset=self.size * (self.page),
            include_total=True,
        )


class JSONAPIPage(AbstractPage[T], Generic[T]):
    page: GreaterEqualOne
    size: GreaterEqualOne
    pages: GreaterEqualZero | None = None

    __params_type__ = JSONAPIParams

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        params: AbstractParams,
        *,
        total: int | None = None,
        **kwargs: Any,
    ) -> Self:
        if not isinstance(params, JSONAPIParams):
            raise TypeError('параметры для страницы некорректно сформированы')

        size = params.size if params.size is not None else total
        page = params.page if params.page is not None else 0

        if size == 0:
            pages = 0
        elif total is not None:
            pages = ceil(total / size)
        else:
            pages = None

        return create_pydantic_model(
            cls,
            total=total,
            items=items,
            page=page,
            size=size,
            pages=pages,
            **kwargs,
        )
