from pydantic import BaseSettings, Field
from dotenv import load_dotenv
import types
import os

load_dotenv()


class BaseDBSettings(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class PostgresSettings(BaseDBSettings):
    """ Параметры подключения к БД Postgres """
    dbname: str = Field(env='DB_NAME')
    host: str = Field(env='DB_HOST')
    port: int = Field(default=5432, env='DB_PORT')
    user: str = Field(env='POSTGRES_USER')
    password: str = Field(env='POSTGRES_PASSWORD')
    options: str = '-c search_path=content'


class RedisSettings(BaseDBSettings):
    database_name: int = Field(default=0)
    host: str = Field(default='localhost', env='REDIS_HOST')
    port: int = Field(default=6379, env='REDIS_PORT')


class ElasticSettings(BaseDBSettings):
    """ Параметры подключения к БД Elasticsearch """
    host_name: str = Field(default='http://localhost:9200', env='ES_HOST')


PG_PARAMS = PostgresSettings().dict()
REDIS_PARAMS = RedisSettings().dict()
ES_PARAMS = ElasticSettings().dict()

DSL = types.MappingProxyType(
    {'dbname': os.getenv('DB_NAME'),
     'user': os.getenv('POSTGRES_USER'),
     'password': os.getenv('POSTGRES_PASSWORD'),
     'host': os.getenv('DB_HOST'),
     'port': os.getenv('DB_PORT'),
     },
)