# -*- coding: utf-8 -*-
import re
from itertools import zip_longest

from werkzeug.exceptions import NotFound


def data_pagination(data: list, page: int, page_size: int) -> list:
    """Pagination of a dataset data.

    Args:
        data (list): a list of rows from dataset csv
        page (int): requested page. Initial page is 1.
        page_size (int): total of items per page

    Raises:
        NotFound: whenever a dataset does not contain records or the requested page number

    Returns:
        list: a list with requested page data
    """
    split_into_pages = list(list(zip_longest(*(iter(data),) * page_size)))

    try:
        if all(split_into_pages[page - 1]):
            return split_into_pages[page - 1]
        elif split_into_pages[page - 1]:
            return list(filter(None, split_into_pages[page - 1]))
        else:
            raise NotFound("The informed page does not contain records")
    except IndexError:
        raise NotFound("The specified page does not exist")


def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
