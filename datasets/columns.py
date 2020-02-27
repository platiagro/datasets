# -*- coding: utf-8 -*-
from platiagro import load_dataset, save_dataset, load_metadata
from werkzeug.exceptions import BadRequest, NotFound

from platiagro.featuretypes import validate_featuretypes


def list_columns(dataset):
    """Lists all columns from a dataset.

    Args:
        dataset: the dataset name.

    Returns:
        A list of columns names and dtypes.
    """
    columns = []
    try:
        df = load_dataset(dataset)
        metadata = load_metadata(dataset)

        names = df.columns.tolist()
        featuretypes = metadata["featuretypes"]

        for name, ftype in zip(names, featuretypes):
            columns.append({
                "name": name,
                "featuretype": ftype,
            })
    except FileNotFoundError:
        raise NotFound("The specified dataset does not exist")

    return columns


def update_column(dataset, column, featuretype):
    """Updates a column from a dataset.

    Args:
        dataset: the dataset name.
        column: the column name.
        featuretype: the feature type (Numerical, Categorical, or DateTime).

    Returns:
        The column info.
    """
    try:
        df = load_dataset(dataset)
        metadata = load_metadata(dataset)

        columns = df.columns.tolist()
        featuretypes = metadata["featuretypes"]

        if column not in columns:
            raise NotFound("The specified column does not exist")

        # sets new metadata
        idx = columns.index(column)
        featuretypes[idx] = featuretype

        validate_featuretypes(featuretypes)

        metadata["featuretypes"] = featuretypes

        ## uses PlatIAgro SDK to save the dataset
        save_dataset(dataset, df, metadata=metadata)

    except FileNotFoundError as e:
        raise NotFound("The specified dataset does not exist")
    except ValueError as e:
        raise BadRequest(str(e))

    return {"name": column, "featuretype": featuretype}
