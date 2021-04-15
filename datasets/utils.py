# -*- coding: utf-8 -*-
"""Utility functions."""
import re
from itertools import zip_longest

from datasets.exceptions import NotFound


def data_pagination(content, page, page_size):
    """
    Pagination of a dataset content.

    Parameters
    ----------
    content : list
    page : int
    page_size : int

    Raises
    ------
    NotFound
        Whenever a dataset does not contain records or the requested page number.

    Returns
    --------
    list
        A list with requested page data.
    """
    # Splits records into `page_size` size
    split_into_pages = list(list(zip_longest(*(iter(content),) * abs(page_size))))

    try:
        # if the last page is not filled (has the length of page_size), `zip_longest`
        # fills with None values. Remove these values before returning
        paged_data = list(filter(None, split_into_pages[page-1]))
    except IndexError:
        raise NotFound("The specified page does not exist")

    return paged_data


def to_snake_case(name):
    """
    Convert string to snake case.

    Parameters
    ----------
    name : str

    Returns
    -------
    str
        The given string in snake case.
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
