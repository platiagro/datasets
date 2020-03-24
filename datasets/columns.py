# -*- coding: utf-8 -*-
from platiagro import load_dataset, save_dataset, stat_dataset
from werkzeug.exceptions import BadRequest, NotFound

from platiagro.featuretypes import infer_featuretypes, validate_featuretypes


def list_columns(dataset):
    """Lists all columns from a dataset.

    Args:
        dataset (str): the dataset name.

    Returns:
        A list of columns names and featuretypes.
    """
    try:
        metadata = stat_dataset(dataset)

        try:
            columns = metadata["columns"]
            featuretypes = metadata["featuretypes"]
        except KeyError:
            df = load_dataset(dataset)
            columns = df.columns.tolist()
            featuretypes = infer_featuretypes(df)

        columns = [{"name": col, "featuretype": ftype} for col, ftype in zip(columns, featuretypes)]
        return columns
    except FileNotFoundError:
        raise NotFound("The specified dataset does not exist")


def update_column(dataset, column, featuretype):
    """Updates a column from a dataset.

    Args:
        dataset (str): the dataset name.
        column (str): the column name.
        featuretype (str): the feature type (Numerical, Categorical, or DateTime).

    Returns:
        The column info.
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
