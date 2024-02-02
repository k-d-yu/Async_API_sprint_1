from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Nested, QueryString, Term, Terms


def films_by_person(person: dict) -> dict:
    query = Search().filter(
        Nested(path='actors', query=Term(actors__id=person['id'])) |
        Nested(path='writers', query=Term(writers__id=person['id'])) |
        Nested(path='directors', query=Term(directors__id=person['id'])),
    )
    return query.to_dict()


def films_by_name(name: str) -> dict:
    query = Search().filter(
        Nested(path='actors', query=QueryString(query=name, fields=['actors.name']), inner_hits={}) |
        Nested(path='writers', query=QueryString(query=name, fields=['writers.name']), inner_hits={}) |
        Nested(path='directors', query=QueryString(query=name, fields=['directors.name']), inner_hits={}),
    )
    return query.to_dict()


def persons_by_query(query: str, fields: list):
    query = Search().filter(QueryString(query=query, fields=fields))
    return query.to_dict()
