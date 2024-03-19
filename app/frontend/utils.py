import math


def frontend_pagination(page, items, count, path):
    total = math.ceil(count / items)
    pagination = range(page - 3, page + 4)
    pagination = [item for item in pagination if item >= 1 and item <= total]
    previous_page = page - 1 if page != 1 else None
    next_page = page + 1 if page != total else None

    return {
        "total": total,
        "current": page,
        "pages": pagination,
        "previous": previous_page,
        "next": next_page,
        "path": path,
    }


def pagination(page, size=100):
    limit = size
    offset = (limit * (page)) - limit

    return limit, offset
