from itertools import zip_longest
from werkzeug.exceptions import NotFound


def data_pagination(data: list, page: int, page_size: int) -> list:
    """Pagination of a dataset data.

    Args:
        data (list): a list of rows from dataset csv
        page (int): requested page
        page_size (int): total of items per page

    Raises:
        NotFound: whenever a dataset does not contain records or the requested page number

    Returns:
        list: a list with requested page data
    """

    split_into_pages = list(list(zip_longest(*(iter(data),) * page_size)))

    try:
        if all(split_into_pages[page]):
            return split_into_pages[page]
        elif split_into_pages[page]:
            return list(filter(None, split_into_pages[page]))
        else:
            raise NotFound("The informed page does not contain records")
    except IndexError:
        raise NotFound("The specified page does not exist")
