import random
from contextlib import contextmanager
from typing import Iterator

import psycopg2
from classes.models import (Filmwork, Genre, GenreFilmwork, Person,
                            PersonFilmwork)
from classes.postgresLoader import PostgresSaver
from faker import Faker
from misc.config import DSL, SIZE, REDIS_PARAMS
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from redis import Redis
from misc.state import State, RedisStorage


@contextmanager
def open_close_postgres(**dsn) -> Iterator[_connection]:
    """Инициализация подключения к БД, закрытие соединения.

    Args:
        dsn: Параметры подключения к БД;

    Yields:
        Iterator: Соединение с БД.
    """
    conn = psycopg2.connect(**dsn)
    conn.cursor_factory = DictCursor
    yield conn
    conn.close()


def connect_to_redis(database_name: int, host: str, port: int) -> Redis:
    return Redis(db=database_name, host=host, port=port)


def data_from_faker(pg_conn: _connection, state: State):
    """Основной метод загрузки данных в Postgres.

    Args:
        pg_conn: Объект связи с БД Postgres.

    """
    db_not_created = state.get_state('db_not_created', True)

    if db_not_created:

        # TODO : сделать красивее
        faker = Faker()
        Faker.seed(13)
        postgres_saver = PostgresSaver(pg_conn)
        filmwork_ids, person_ids, genre_ids = [], [], []
        list_genres, list_persons, list_filmworks = [], [], []
        filmworks_genres, filmworks_persons = [], []

        for i in range(1, SIZE * 10):
            created_date = faker.date_between(start_date='-90y', end_date='-1w')
            genre_id = faker.uuid4()
            genre_ids.append(genre_id)
            list_genres.append(
                Genre(
                    genre_id,
                    created_date,
                    faker.date_between(start_date=created_date, end_date='now'),
                    faker.bs(),
                    faker.paragraph(nb_sentences=5),
                ).__dict__,
            )
        postgres_saver.load_data('genre', [list_genres], Genre)
        postgres_saver.postgres.commit()
        postgres_saver.cursor.execute('deallocate all;')

        for i in range(0, SIZE * 10):
            temp_list = []
            for j in range(0, SIZE):
                created_date = faker.date_between(start_date='-90y', end_date='-1w')
                person_id = faker.uuid4()
                person_ids.append(person_id)
                temp_list.append(
                    Person(
                        person_id,
                        created_date,
                        faker.date_between(start_date=created_date, end_date='now'),
                        faker.name(),
                    ).__dict__,
                )
            list_persons.append(temp_list)
        postgres_saver.load_data('person', list_persons, Person)
        postgres_saver.postgres.commit()
        postgres_saver.cursor.execute('deallocate all;')

        for i in range(0, SIZE * 100):
            temp_list = []
            for j in range(0, SIZE):
                created_date = faker.date_between(start_date='-50y', end_date='-1w')
                film_id = faker.uuid4()
                filmwork_ids.append(film_id)
                temp_list.append(
                    Filmwork(
                        film_id,
                        created_date,
                        faker.date_between(start_date=created_date, end_date='now'),
                        faker.catch_phrase(),
                        faker.random_element(elements=['tv_show', 'movie']),
                        faker.paragraph(nb_sentences=7),
                        faker.date_between(start_date='-110y', end_date=created_date),
                        random.uniform(0.0, 10.0),
                    ).__dict__,
                    )
            list_filmworks.append(temp_list)
        postgres_saver.load_data('film_work', list_filmworks, Filmwork)
        postgres_saver.postgres.commit()
        postgres_saver.cursor.execute('deallocate all;')

        for film_work in filmwork_ids:
            i = random.randint(0, 7)
            temp_list = []
            current_film_genres = faker.random_elements(genre_ids, length=i, unique=True)
            for ids in current_film_genres:
                created_date = faker.date_between(start_date='-50y', end_date='-1w')
                temp_list.append(
                    GenreFilmwork(
                        faker.uuid4(),
                        created_date,
                        ids,
                        film_work
                    ).__dict__
                )
            filmworks_genres.append(temp_list)

            i = random.randint(0, 27)
            temp_list = []
            current_film_persons = faker.random_elements(person_ids, length=i, unique=True)
            for ids in current_film_persons:
                created_date = faker.date_between(start_date='-50y', end_date='-1w')
                temp_list.append(
                    PersonFilmwork(
                        faker.uuid4(),
                        created_date,
                        ids,
                        film_work,
                        faker.random_element(elements=['director', 'writer', 'actor'])
                    ).__dict__
                )
            filmworks_persons.append(temp_list)
        postgres_saver.load_data('genre_film_work', filmworks_genres, GenreFilmwork)
        postgres_saver.postgres.commit()
        postgres_saver.cursor.execute('deallocate all;')

        postgres_saver.load_data('person_film_work', filmworks_persons, PersonFilmwork)
        postgres_saver.postgres.commit()
        postgres_saver.cursor.execute('deallocate all;')
        state.set_state('db_not_created', False)


if __name__ == '__main__':
    with open_close_postgres(**DSL) as pg_conn:
        with connect_to_redis(**REDIS_PARAMS) as re_conn:
            state = State(RedisStorage(re_conn))
            data_from_faker(pg_conn, state)
