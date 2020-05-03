# -*- coding: utf-8 -*-
from typing import Dict, List

from platiagro import load_dataset, save_dataset, stat_dataset
from platiagro.featuretypes import validate_featuretypes
from werkzeug.exceptions import BadRequest, NotFound


def list_columns(dataset: str) -> List[Dict[str, str]]:
    """Lists all columns from a dataset.

    Args:
        dataset (str): the dataset name.

    Returns:
        A list of columns names and featuretypes.

    Raises:
        NotFound: when the dataset does not exist.
    """
    try:
        metadata = stat_dataset(dataset)

        columns = metadata["columns"]
        featuretypes = metadata["featuretypes"]

        columns = [{"name": col, "featuretype": ftype} for col, ftype in zip(columns, featuretypes)]
        return columns
    except FileNotFoundError:
        raise NotFound("The specified dataset does not exist")


def update_column(dataset: str, column: str, featuretype: str) -> Dict[str, str]:
    """Updates a column from a dataset.

    Args:
        dataset (str): the dataset name.
        column (str): the column name.
        featuretype (str): the feature type (Numerical, Categorical, or DateTime).

    Returns:
        The column info.

    Raises:
        NotFound: when the dataset or column does not exist.
        BadRequest: when the featuretype is invalid.
    """
    try:
        metadata = stat_dataset(dataset)
        columns = metadata["columns"]

        if column not in columns:
            raise NotFound("The specified column does not exist")

        # sets new metadata
        index = columns.index(column)
        metadata["featuretypes"][index] = featuretype

        validate_featuretypes(metadata["featuretypes"])

        df = load_dataset(dataset)

        # uses PlatIAgro SDK to save the dataset
        save_dataset(dataset, df, metadata=metadata)
    except FileNotFoundError:
        raise NotFound("The specified dataset does not exist")
    except ValueError as e:
        raise BadRequest(str(e))

    return {"name": column, "featuretype": featuretype}
