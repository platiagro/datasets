# -*- coding: utf-8 -*-
from io import StringIO
from os import SEEK_SET
from typing import Any, Dict, IO, List
from uuid import uuid4

import pandas as pd
import platiagro
from chardet.universaldetector import UniversalDetector
from platiagro import save_dataset, stat_dataset
from platiagro.featuretypes import infer_featuretypes, validate_featuretypes
from werkzeug.exceptions import BadRequest, NotFound


def list_datasets() -> List[Dict[str, Any]]:
    """Lists all datasets from our object storage.

    Returns:
        A list of all datasets.
    """
    datasets = platiagro.list_datasets()
    return [get_dataset(name) for name in datasets]


def create_dataset(files: Dict[str, IO]) -> Dict[str, Any]:
    """Creates a new dataset in our object storage.

    Args:
        files (dict): file objects.

    Returns:
        The dataset details: name, columns, and filename.

    Raises:
        BadRequest: when incoming files are missing or valid.
    """
    # checks if the post request has the file part
    if "file" not in files:
        raise BadRequest("No file part")
    file = files["file"]

    # if user does not select file, the browser also
    # submits an empty part without filename
    if file.filename == "":
        raise BadRequest("No selected file")

    # reads file into a DataFrame
    df = read_into_dataframe(file)
    columns = df.columns.values.tolist()

    # checks if the post request has the 'featuretypes' part
    if "featuretypes" in files:
        try:
            ftype_file = files["featuretypes"]
            featuretypes = list(map(lambda s: s.strip().decode("utf8"), ftype_file.readlines()))
            validate_featuretypes(featuretypes)
        except ValueError as e:
            raise BadRequest(str(e))

        if len(columns) != len(featuretypes):
            raise BadRequest("featuretypes must be the same length as the DataFrame columns")
    else:
        featuretypes = infer_featuretypes(df)

    # generates an uuid for the dataset
    name = str(uuid4())

    metadata = {
        "featuretypes": featuretypes,
        "original-filename": file.filename,
    }

    # uses PlatIAgro SDK to save the dataset
    save_dataset(name, df, metadata=metadata)

    columns = [{"name": col, "featuretype": ftype} for col, ftype in zip(columns, featuretypes)]
    return {"name": name, "columns": columns, "filename": file.filename}


def get_dataset(name: str) -> Dict[str, Any]:
    """Details a dataset from our object storage.

    Args:
        name (str): the dataset name to look for in our object storage.

    Returns:
        The dataset details: name, columns, and filename.

    Raises:
        NotFound: when the dataset does not exist.
    """
    try:
        metadata = stat_dataset(name)

        columns = metadata["columns"]
        featuretypes = metadata["featuretypes"]
        filename = metadata.get("original-filename")

        columns = [{"name": col, "featuretype": ftype} for col, ftype in zip(columns, featuretypes)]
        return {"name": name, "columns": columns, "filename": filename}
    except FileNotFoundError:
        raise NotFound("The specified dataset does not exist")


def read_into_dataframe(file: IO, nrows: int = 100, th: float = 0.9) -> pd.DataFrame:
    """Reads a file into a DataFrame.

    Infers the file encoding and whether a header column exists

    Args:
        file (IO): file buffer.
        nrows (int, optional): number of rows to peek. Default: 100.
        th (float, optional): threshold.

    Returns:
        A pandas.DataFrame.
    """
    detector = UniversalDetector()
    for line, text in enumerate(file):
        detector.feed(text)
        if detector.done or line > nrows:
            break
    detector.close()
    encoding = detector.result.get("encoding")

    file.seek(0, SEEK_SET)
    file = StringIO(file.read().decode(encoding))
    df1 = pd.read_csv(file, sep=None, engine="python", header="infer", nrows=nrows)
    file.seek(0, SEEK_SET)
    df2 = pd.read_csv(file, sep=None, engine="python", header=None, nrows=nrows)
    file.seek(0, SEEK_SET)
    sim = (df1.dtypes.values == df2.dtypes.values).mean()
    header = "infer" if sim < th else None
    df = pd.read_csv(file, sep=None, engine="python", header=header, prefix="col")
    file.seek(0, SEEK_SET)
    return df
