import math
from core.config import settings


def get_by_pagination(
    name: str,
    db_objects,
    total: int,
    page: int = settings.page_number,
    page_size: int = settings.page_size,
) -> dict:
    next_page, previous_page = None, None
    if page > 1:
        previous_page = page - 1
    previous_items = (page - 1) * page_size
    if previous_items + len(db_objects) < total:
        next_page = page + 1
    pages: int = int(math.ceil(total / float(page_size)))
    return {
        f"{name}": db_objects,
        "page": page,
        "page_size": page_size,
        "previous_page": previous_page,
        "next_page": next_page,
        "available_pages": pages,
        "total": total,
    }