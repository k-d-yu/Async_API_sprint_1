import os
from logging import config as logging_config
from pydantic import BaseSettings, Field

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):

    project_name: str = 'PRAKTIKUM'
    redis_host: str = ...
    redis_port: int = Field(default=6379)

    elastic_host: str = Field(..., env='ES_HOST')
    elastic_port: int = Field(default=9200, env='ES_PORT')

    max_window_size: int = Field(default=10000)

    page_size: int = Field(default=10, env='DEFAULT_PAGE_SIZE')
    page_number: int = Field(default=1, env='DEFAULT_PAGE_NUMBER')

    cache_lifetime: int = Field(default=60 * 5, env='FILM_CACHE_EXPIRE_IN_SECONDS')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
