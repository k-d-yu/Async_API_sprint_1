"""Вспомогательные константы, классы и функции."""

import logging
import os
from pydantic import BaseSettings, Field
import types
from typing import Type, Union

from classes.models import (Filmwork, Genre, GenreFilmwork, Person,
                            PersonFilmwork)
from dotenv import load_dotenv

load_dotenv()

FORMAT = '%(levelname)s. %(message)s'

LOG_LEVEL = logging.WARNING

SIZE = int(os.getenv('SIZE'))

DSL = types.MappingProxyType(
    {'dbname': os.getenv('DB_NAME'),
     'user': os.getenv('POSTGRES_USER'),
     'password': os.getenv('POSTGRES_PASSWORD'),
     'host': os.getenv('DB_HOST'),
     'port': os.getenv('DB_PORT'),
     },
)

RELATION_DB_TO_CLASSES = types.MappingProxyType(
    {'film_work': Filmwork,
     'genre': Genre,
     'genre_film_work': GenreFilmwork,
     'person': Person,
     'person_film_work': PersonFilmwork,
     },
)

SCHEME = Union[Type[Genre], Type[Person], Type[Filmwork],
               Type[GenreFilmwork], Type[PersonFilmwork]]


class BaseDBSettings(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class RedisSettings(BaseDBSettings):
    database_name: int = Field(default=0)
    host: str = Field(default='localhost', env='REDIS_HOST')
    port: int = Field(default=6379, env='REDIS_PORT')


REDIS_PARAMS = RedisSettings().dict()
