from pydantic import parse_obj_as


def get_params_films_to_elastic(
        page_size: int, page: int, genre: str = None, query: str = None
) -> dict:
    genre_search: list = []
    if genre:
        genre_search.append({"term": {"genre": genre}})
    if query:
        body: dict = {
            "size": page_size,
            "from": (page - 1) * page_size,
            "query": {
                "bool": {
                    "must": {"match": {"title": {"query": query, "fuzziness": "auto"}}},
                    "filter": genre_search,
                }
            },
        }
        return body

    if genre:
        body: dict = {
            "query": {
                "nested": {
                    "path": "genres",
                    "query": {
                        "match": {
                            "genres.name": {
                                "query": genre,
                                "operator": "and"
                            }
                        }
                    }
                }
            }
        }
        return body


def get_hits(docs: dict, models):
    hits: dict = docs.get("hits").get("hits")
    data: list = [row.get("_source") for row in hits]
    parse_data = parse_obj_as(list[models], data)
    return parse_data