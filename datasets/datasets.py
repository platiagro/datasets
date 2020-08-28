# -*- coding: utf-8 -*-
from io import BytesIO
from os import SEEK_SET
from os.path import splitext
from typing import Any, Dict, IO, List
from unicodedata import normalize

import pandas as pd
import platiagro
from chardet.universaldetector import UniversalDetector
from pandas.io.common import infer_compression
from platiagro import save_dataset, stat_dataset, update_dataset_metadata
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

    # generate a dataset name from filename
    name = generate_name(file.filename)

    try:
        # reads file into a DataFrame
        df = read_into_dataframe(file, file.filename)
    except Exception:
        # if read fails, then uploads raw file
        file.seek(0, SEEK_SET)
        save_dataset(name, file)
        return {"name": name, "filename": file.filename}

    columns = df.columns.values.tolist()
    featuretypes = infer_featuretypes(df)

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

        filename = metadata.get("original-filename")

        if "columns" in metadata and "featuretypes" in metadata:
            columns = metadata["columns"]
            featuretypes = metadata["featuretypes"]
            columns = [{"name": col, "featuretype": ftype} for col, ftype in zip(columns, featuretypes)]
            return {"name": name, "columns": columns, "filename": filename}

        return {"name": name, "filename": filename}
    except FileNotFoundError:
        raise NotFound("The specified dataset does not exist")


def patch_dataset(name: str, files: Dict[str, IO]) -> Dict[str, Any]:
    """Update the dataset metadata in our object storage.
    Args:
        name (str): the dataset name to look for in our object storage.
        files (dict): file objects.
    Returns:
        The dataset details: name, columns, and filename.
    Raises:
        BadRequest: when incoming files are missing or invalid.
        NotFound: when the dataset does not exist
    """
    if "featuretypes" not in files:
        raise BadRequest("No featuretypes part")

    try:
        metadata = stat_dataset(name)
    except FileNotFoundError:
        raise NotFound("The specified dataset does not exist")

    try:
        ftype_file = files["featuretypes"]
        featuretypes = list(map(lambda s: s.strip().decode("utf8"), ftype_file.readlines()))
        validate_featuretypes(featuretypes)
    except ValueError as e:
        raise BadRequest(str(e))

    columns = metadata["columns"]
    if len(columns) != len(featuretypes):
        raise BadRequest("featuretypes must be the same length as the DataFrame columns")

    # uses PlatIAgro SDK to update the dataset metadata
    metadata["featuretypes"] = featuretypes
    update_dataset_metadata(name=name, metadata=metadata)
    return get_dataset(name)


def read_into_dataframe(file: IO,
                        filename: str = "",
                        nrows: int = 100,
                        max_characters: int = 50) -> pd.DataFrame:
    """Reads a file into a DataFrame.
    Infers the file encoding and whether a header column exists
    Args:
        file (IO): file buffer.
        filename (str): filename. Used to infer compression.
        nrows (int, optional): number of rows to peek. Default: 100.
        max_characters (int, optional): max characters a column name can have to be distinguished from a real text value
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

    compression = infer_compression(filename, "infer")

    file.seek(0, SEEK_SET)
    contents = file.read()

    with BytesIO(contents) as file:
        df0 = pd.read_csv(
            file,
            encoding=encoding,
            compression=compression,
            sep=None,
            engine="python",
            header="infer",
            nrows=nrows,
        )

    df0_cols = list(df0.columns)

    # Check if all columns are strings and short strings(text values tend to be long)
    column_names_checker = all([type(item) == str for item in df0_cols])
    if column_names_checker:
        column_names_checker = all([len(item) < max_characters for item in df0_cols])

    # Check if any column can be turned to float
    conversion_checker = True
    for item in df0_cols:
        try:
            item = float(item)
            conversion_checker = False
            break
        except ValueError:
            pass

    # Prefix and header
    final_checker = True if (column_names_checker and conversion_checker) else False
    header = "infer" if final_checker else None
    prefix = None if header else "col"

    with BytesIO(contents) as file:
        df = pd.read_csv(
            file,
            encoding=encoding,
            compression=compression,
            sep=None,
            engine="python",
            header=header,
            prefix=prefix,
        )
    return df


def generate_name(filename: str, attempt: int = 1) -> str:
    """Generates a dataset name from a given filename.

    Args:
        filename (str): source filename.
        attempt (int): the current attempt of generating a new name.

    Return:
        str: new generated dataset name.
    """
    # normalize filename to ASCII characters
    # replace spaces by dashes
    name = normalize('NFKD', filename) \
        .encode('ASCII', 'ignore') \
        .replace(b' ', b'-') \
        .decode()

    if attempt > 1:
        # adds a suffix '-NUMBER' to filename
        name, extension = splitext(name)
        name = f"{name}-{attempt}{extension}"

    try:
        # check if final_name is already in use
        stat_dataset(name)
    except FileNotFoundError:
        return name

    # if it is already in use,
    return generate_name(filename, attempt + 1)
