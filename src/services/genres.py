from core.base_search import BaseSearch


class GenreSearch(BaseSearch):

    async def list(self, query):
        genres = await super().search_list_of_docs(query)
        return genres
