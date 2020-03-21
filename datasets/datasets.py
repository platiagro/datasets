# -*- coding: utf-8 -*-
from os import SEEK_SET
from uuid import uuid4

import pandas as pd
import platiagro
from platiagro import save_dataset, load_metadata
from platiagro.featuretypes import infer_featuretypes, validate_featuretypes
from werkzeug.exceptions import BadRequest, NotFound


def list_datasets():
    """Lists all datasets from our object storage.

    Returns:
        A list of all datasets.
    """
    datasets = platiagro.list_datasets()
    return [get_dataset(name) for name in datasets]


def create_dataset(files):
    """Creates a new dataset in our object storage.

    Args:
        files (dict): file objects.

    Returns:
        The dataset info.
    """
    # checks if the post request has the file part
    if "file" not in files:
        raise BadRequest("No file part")
    file = files["file"]

    # if user does not select file, the browser also
    # submits an empty part without filename
    if file.filename == "":
        raise BadRequest("No selected file")

    # reads csv file into a DataFrame
    df = read_csv(file)
    columns = df.columns.values.tolist()

    # checks if the post request has the 'featuretypes' part
    if "featuretypes" in files:
        ftype_file = files["featuretypes"]
        featuretypes = list(map(lambda s: s.strip().decode("utf8"), ftype_file.readlines()))
        validate_featuretypes(featuretypes)
    else:
        featuretypes = infer_featuretypes(df)

    # generates an uuid for the dataset
    name = str(uuid4())

    metadata = {
        "featuretypes": featuretypes,
        "filename": file.filename,
    }

    # uses PlatIAgro SDK to save the dataset
    save_dataset(name, df, metadata=metadata)

    columns = [{"name": col, "featuretype": ftype} for col, ftype in zip(columns, featuretypes)]
    return {"name": name, "columns": columns, "filename": file.filename}


def get_dataset(name):
    """Details a dataset from our object storage.

    Args:
        name (str): the dataset name to look for in our object storage.

    Returns:
        The dataset info.
    """
    try:
        metadata = load_metadata(name)

        columns = metadata["columns"]
        featuretypes = metadata["featuretypes"]
        filename = metadata["filename"]
        columns = [{"name": col, "featuretype": ftype} for col, ftype in zip(columns, featuretypes)]
        return {"name": name, "columns": columns, "filename": filename}
    except FileNotFoundError:
        raise NotFound("The specified dataset does not exist")


def read_csv(file, nrows=5, th=0.9):
    """Read a csv file into a DataFrame. Infers whether a header column exists.

    Args:
        file (IO): filepath or buffer.
        nrows (int, optional): number of rows to peek. Default: 5.
        th (float, optional): threshold.

    Returns:
        A pandas.DataFrame.
    """
    df1 = pd.read_csv(file, header="infer", nrows=nrows)
    file.seek(0, SEEK_SET)
    df2 = pd.read_csv(file, header=None, nrows=nrows)
    file.seek(0, SEEK_SET)
    sim = (df1.dtypes.values == df2.dtypes.values).mean()
    header = "infer" if sim < th else None
    df = pd.read_csv(file, header=header, prefix="col")
    file.seek(0, SEEK_SET)
    return df
