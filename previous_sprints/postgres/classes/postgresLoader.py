"""Загрузка данных в БД Postgres."""

import logging
from dataclasses import dataclass

from misc.config import FORMAT, LOG_LEVEL, SCHEME
from psycopg2 import IntegrityError, sql
from psycopg2.extensions import connection as _connect
from psycopg2.extras import execute_batch

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)
logger = logging.getLogger()


@dataclass
class PostgresSaver(object):
    """Класс для выполнения манипуляций с БД Postgres."""

    postgres: _connect

    def __post_init__(self):
        """После инициализации экземпляра cоздается объект курсора."""
        self.cursor = self.postgres.cursor()

    def load_data(self, table_name, batches_pack, schema: SCHEME):
        batches_count = 0

        column_names = schema.__match_args__
        try:
            for block in batches_pack:
                keys = column_names
                preparation = """prepare stmnt_{num} as
                                 insert into {table} ({columns}) values({params});
                """
                batch_records = []
                for rec in block:
                    batch_records.append(tuple(rec[key] for key in keys))
                batches_count += 1
                exec_query = sql.SQL('execute stmnt_{cnt} ({args});').format(
                    args=sql.SQL(', ').join(
                        map(sql.Placeholder, keys),
                    ),
                    cnt=sql.Literal(batches_count),
                )
                self.cursor.execute(sql.SQL(preparation).format(
                    table=sql.Identifier(table_name),
                    columns=sql.SQL(',').join([sql.Identifier(field) for field in keys]),
                    params=sql.SQL(', ').join(
                        sql.SQL(
                            '${0}',
                        ).format(sql.Literal(field)) for field in range(1, len(keys) + 1)
                    ),
                    num=sql.Literal(batches_count),
                ))
                execute_batch(self.cursor, exec_query, block)
                logger.info(
                    'Batch #{num}: вставка в таблицу '
                    '{table_name} успешна.'.format(
                        num=batches_count, table_name=table_name,
                    ),
                )
        except IntegrityError as err:
            if 'unique constraint' in str(err):
                logger.error(
                    'Table {table_name}, batch #{num} : несоответствие '
                    'записи ключу уникальности.'.format(table_name=table_name, num=batches_count),
                )
                raise err

