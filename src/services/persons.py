from core.base_search import BaseSearch


class PersonSearch(BaseSearch):

    async def list(self, query):
        persons = await super().search_list_of_docs(query)
        return persons
