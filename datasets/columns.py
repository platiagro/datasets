# -*- coding: utf-8 -*-
from platiagro import load_dataset, save_dataset, stat_dataset
from platiagro.featuretypes import validate_featuretypes
from datasets.exceptions import BadRequest, NotFound

COLUMN_NOT_FOUND = NotFound("ColumnNotFound", "The specified column does not exist")
DATASET_NOT_FOUND = NotFound("DatasetNotFound", "The specified dataset does not exist")


def list_columns(dataset):
    """
    Lists all columns from a dataset.

    Parameters
    ----------
    dataset : str
        The dataset name.

    Returns
    -------
    list
        A list of columns names and featuretypes.

    Raises
    ------
    NotFound
        When the dataset does not exist.
    """
    try:
        metadata = stat_dataset(dataset)

        columns = metadata.get("columns", [])
        featuretypes = metadata.get("featuretypes", [])

        columns = [{"name": col, "featuretype": ftype} for col, ftype in zip(columns, featuretypes)]
        return columns
    except FileNotFoundError:
        raise DATASET_NOT_FOUND


def update_column(dataset, column, featuretype):
    """
    Updates a column from a dataset.

    Paramters
    ---------
    dataset : str
        The dataset name.
    column : str
        The column name.
    featuretype : str
        The feature type (Numerical, Categorical, or DateTime).

    Returns
    -------
    dict
        The column info.

    Raises
    ------
    NotFound
        When the dataset or column does not exist.

    BadRequest
        When the featuretype is invalid.
    """
    try:
        metadata = stat_dataset(dataset)

        if "columns" not in metadata or "featuretypes" not in metadata:
            raise COLUMN_NOT_FOUND

        columns = metadata["columns"]

        if column not in columns:
            raise COLUMN_NOT_FOUND

        # sets new metadata
        index = columns.index(column)
        metadata["featuretypes"][index] = featuretype

        validate_featuretypes(metadata["featuretypes"])

        df = load_dataset(dataset)

        # uses PlatIAgro SDK to save the dataset
        save_dataset(dataset, df, metadata=metadata)
    except FileNotFoundError:
        raise DATASET_NOT_FOUND
    except ValueError as e:
        raise BadRequest("ValueError", str(e))

    return {"name": column, "featuretype": featuretype}
