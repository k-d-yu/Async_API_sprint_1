import datetime
import json
import logging
import time
from typing import List
import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from dotenv import load_dotenv
import os
from psycopg2 import OperationalError
import backoff
from state import State, JsonFileStorage
from misc import PG_PARAMS, DSL
import requests
from requests.exceptions import ConnectionError
from contextlib import closing
import queries

load_dotenv()

logging.basicConfig(level=logging.INFO, filename="transfer.log", filemode="w")

# Флаг, который определяет, запущена ли функция переноса данных
running_flag = False


def pg_to_etl(pg_conn: _connection, etl_url: str) -> None:
    """
    Получает данные из Postgress и сохраняет их в ElasticSearch
    :param pg_conn: соединение с Postgress
    :param etl_url: ссылка на Elasticsearch
    :return: результат выполнения функции
    """
    logging.info('Начало загрузки данных')

    state = State(JsonFileStorage('state.json'))

    last_update = state.get_state('last_update') if state.get_state('last_update') else '1900-01-01'

    logging.info('Дата последнего обновления: ' + last_update)

    pg = PostgresExtract(pg_conn, size=1000, last_update=last_update)

    es = Es(etl_url)

    for item in ['persons', 'genres', 'movies']:
        logging.info(f'Загрузка данных: {item}')
        for rows in pg.get_data(item):

            logging.info(f'Количество полученных строк: {len(rows)}')

            last_update = es.save(rows, index=item)

            state.set_state('last_update', str(last_update))

        logging.info('Конец загрузки данных')


class Es:
    def __init__(self, url: str):
        self.url = url

    @backoff.on_exception(backoff.expo,
                          ConnectionError)
    def save(self, rows: list, index: str) -> datetime:
        """
        Сохраняет данные в Elasticsearch
        :param index: название индекса
        :param rows: данные
        :return: дата последнего обновления
        """

        results = []

        for item in rows:
            results.append(
                '\n{"index": {"_index": "' + index + '", "_id": "' + item['id'] + '"}}'
            )

            result = self.convert(item, index)

            results.append(json.dumps(result))

        headers = {
            'Content-Type': 'application/x-ndjson',
        }
        data = "\n".join(results) + '\n'

        response = requests.post(self.url + index + '/_bulk', headers=headers, data=data)

        logging.info(f'Обновлено строк: {len(response.json()["items"])}')

        if index == 'movies':
            last_update = max(
                max([row['fw_modified'] for row in rows if row['fw_modified']]),
                max([row['p_modified'] for row in rows if row['p_modified']]),
                max([row['g_modified'] for row in rows if row['g_modified']]),
            )
        else:
            last_update = max([row['modified'] for row in rows if row['modified']])

        return last_update

    def convert(self, item: dict, index: str) -> dict:
        """
        Конвертирует данные  в формат для сохранения в ES
        :param item: объект, который нужно конвертировать (фильм, жанр, персона)
        :param index: название индекса
        :return:
        """
        result = {}
        if index == 'movies':
            directors = []
            actors = []
            writers = []
            for person in item['persons']:
                if person['person_role'] == 'director':
                    directors.append({'id': person['person_id'], 'name': person['person_name']})
                elif person['person_role'] == 'actor':
                    actors.append({'id': person['person_id'], 'name': person['person_name']})
                elif person['person_role'] == 'writer':
                    writers.append({'id': person['person_id'], 'name': person['person_name']})
            result = {
                'id': item['id'],
                'imdb_rating': float(item['rating']),
                'genres': item['genres'],
                'title': item['title'],
                'description': item['description'],
                'directors': directors,
                'actors': actors,
                'writers': writers,
                'actors_names': [actor['name'] for actor in actors],
                'writers_names': [writer['name'] for writer in writers],
            }
        elif index == 'persons':
            result = {
                'id': item['id'],
                'full_name': item['full_name']
            }
        elif index == 'genres':
            result = {
                'id': item['id'],
                'name': item['name'],
                'description': item['description']
            }
        return result


class PostgresExtract:

    def __init__(self, conn: _connection, size: int, last_update: datetime):
        self.conn = conn
        self.size = size
        self.last_update = last_update

    def get_data(self, table: str) -> List[dict]:
        """
        Получает свежие данные из Postgres
        :param table: название таблицы, откуда нужны данные
        :return: реузльтаты запроса из базы данных
        """
        cursor = self.conn.cursor()

        cursor.execute(self.get_query(table))

        while rows := cursor.fetchmany(self.size):
            yield rows
        cursor.close()

    def get_query(self, table: str) -> str:
        """
        Возвратащет строку запроса в зависимость от таблицы
        :param table: название таблицы, откуда нужны данные
        :return: строки с базы данных
        """
        query: str = ''
        if table == 'movies':
            query = queries.movies_query % {'last_update': self.last_update}
        elif table == 'persons':
            query = queries.persons_query % {'last_update': self.last_update}
        elif table == 'genres':
            query = queries.genres_query % {'last_update': self.last_update}
        return query


@backoff.on_exception(backoff.expo,
                      OperationalError)
def pg_connect(**dsl):
    logging.info("Connecting to PostgreSQL database...")
    conn = psycopg2.connect(**dsl, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


if __name__ == '__main__':
    """
    Подключается к базе данных Postgres, получает свежие данные и сохраняет в Elasticsearch
    """
    dsl = {'dbname': os.getenv('DB_NAME'),
           'user': os.getenv('DB_USER'),
           'password': os.getenv('DB_PASSWORD'),
           'host': os.getenv('DB_HOST'),
           'port': os.getenv('PORT')}
    etl_url = os.getenv('ES_URL')
    logging.info(f'Оconn {PG_PARAMS}')

    while True:
        if not running_flag:
            running_flag = True
            with closing(pg_connect(**DSL)) as pg_conn:
                pg_to_etl(pg_conn, etl_url)
                running_flag = False

        time.sleep(60)
