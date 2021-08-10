# -*- coding: utf-8 -*-
import json
from io import BytesIO, TextIOWrapper
from os import SEEK_SET
from os.path import splitext
from unicodedata import normalize
from uuid import uuid4

import numpy as np
import pandas as pd
import datasets.monkeypatch
import platiagro
from chardet.universaldetector import UniversalDetector
from googleapiclient.discovery import build
from googleapiclient.http import HttpError, MediaIoBaseDownload
from oauth2client import client, GOOGLE_TOKEN_URI
from pandas.io.common import infer_compression
from platiagro import load_dataset, save_dataset, stat_dataset, update_dataset_metadata
from platiagro.featuretypes import infer_featuretypes, validate_featuretypes
from datasets.exceptions import BadRequest, NotFound

from datasets.utils import data_pagination

NOT_FOUND = NotFound("The specified dataset does not exist")


def list_datasets():
    """
    Lists all datasets from our object storage.

    Returns
    -------
    List[Dict[str, Any]]
        A list of all datasets.
    """
    datasets = platiagro.list_datasets()
    return [{'name': name} for name in datasets]


def create_dataset(file_object):
    """
    Creates a new dataset in our object storage.

    Parameters
    ----------
    file_object : dict or fastapi.File
        file objects.

    Returns
    -------
    dict
        The dataset details: name, columns, and filename.

    Raises
    -------
    BadRequest
        When incoming files are missing or valid.
    """
    if isinstance(file_object, dict):
        file = file_object["file"]
        filename = file.filename
    else:
        file = file_object.file
        filename = file_object.filename

    # if user does not select file, the browser also
    # submits an empty part without filename
    if filename == "":
        raise BadRequest("No selected file.")

    # generate a dataset name from filename
    name = generate_name(filename)

    try:
        # reads file into a DataFrame
        df = read_into_dataframe(file, filename)
    except Exception:
        # if read fails, then uploads raw file
        file.seek(0, SEEK_SET)
        save_dataset(name, file, metadata={"original-filename": filename})
        return {"name": name, "filename": filename}

    columns = df.columns.values.tolist()
    featuretypes = infer_featuretypes(df)

    metadata = {
        "columns": columns,
        "featuretypes": featuretypes,
        "original-filename": filename,
        "total": len(df.index),
    }

    file.seek(0, SEEK_SET)
    contents = BytesIO(file.read())
    # uses PlatIAgro SDK to save the dataset
    save_dataset(name, contents, metadata=metadata)

    columns = [{"name": col, "featuretype": ftype} for col, ftype in zip(columns, featuretypes)]

    # Replaces NaN value by a text "NaN" so JSON encode doesn't fail
    df.replace(np.nan, "NaN", inplace=True, regex=True)
    df.replace(np.inf, "Inf", inplace=True, regex=True)
    df.replace(-np.inf, "-Inf", inplace=True, regex=True)
    data = df.values.tolist()
    return {"name": name, "columns": columns, "data": data, "total": len(df.index), "filename": filename}


def create_google_drive_dataset(gfile):
    """
    Download the google drive file and creates a new dataset in our object storage.

    Parameters
    ----------
    gfile : dict
        Google Drive file.

    Returns
    -------
    dict
        The dataset details: name, columns, and filename.

    Raises
    ------
    BadRequest
        When a error occurred when trying to retrive file such as: Invalid token or HTTP request.

    NotFound
        When a file was not found.
    """
    client_id = gfile['clientId']
    client_secret = gfile['clientSecret']
    file_id = gfile['id']
    file_name = gfile['name']
    mime_type = gfile['mimeType']
    token = gfile['token']

    credentials = client.OAuth2Credentials(
        access_token=token,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=token,
        token_expiry=None,
        token_uri=GOOGLE_TOKEN_URI,
        user_agent=None)

    service = build('drive', 'v3', credentials=credentials)

    if 'google' in mime_type:
        export_mine_type = 'text/plain'
        if 'spreadsheet' in mime_type:
            export_mine_type = 'text/csv'
        request = service.files().export(fileId=file_id, mimeType=export_mine_type)
    else:
        request = service.files().get_media(fileId=file_id)

    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    try:
        while done is False:
            status, done = downloader.next_chunk()
        fh.filename = file_name
        return create_dataset({'file': fh})
    except client.HttpAccessTokenRefreshError:
        raise BadRequest('Invalid token: client unauthorized')
    except HttpError as e:
        reason = json.loads(e.content).get('error').get('errors')[0].get('message')
        if e.resp.status == 404:
            raise NotFound(reason)
        raise BadRequest(reason)


def get_dataset(name, page=1, page_size=10):
    """
    Details a dataset from our object storage.

    Parameters
    ----------
    name : str
        The dataset name to look for in our object storage.
    page : int or str
        The page number. First page is 1. Default to 1.
    page_size : int or str
        The page size. Default value is 10.

    Returns
    -------
    dict
        The dataset details: name, columns, and filename.

    Raises
    ------
    NotFound
        When the dataset does not exist.
    """
    try:
        page, page_size = int(page), int(page_size)
        metadata = stat_dataset(name)
        filename = metadata.get("original-filename")
        dataset = {"name": name, "filename": filename}

        if "columns" in metadata and "featuretypes" in metadata:
            columns = metadata["columns"]
            featuretypes = metadata["featuretypes"]
            columns = [{"name": col, "featuretype": ftype} for col, ftype in zip(columns, featuretypes)]
            content = load_dataset(name)
            # Replaces NaN value by a text "NaN" so JSON encode doesn't fail
            content.replace(np.nan, "NaN", inplace=True, regex=True)
            content.replace(np.inf, "Inf", inplace=True, regex=True)
            content.replace(-np.inf, "-Inf", inplace=True, regex=True)
            data = content.values.tolist()

            if page_size != -1:
                data = data_pagination(content=data, page=page, page_size=page_size)

            dataset.update({"columns": columns, "data": data, "total": len(content.index)})
        return dataset
    except FileNotFoundError:
        raise NOT_FOUND
    except ValueError:
        raise BadRequest("Invalid parameters")


def patch_dataset(name, file_object):
    """
    Update the dataset metadata in our object storage.

    Parameters
    ----------
    name : str
        The dataset name to look for in our object storage.

    file_object : dict
        File object.

    Returns
    -------
    dict
        The dataset details: name, columns, and filename.

    Raises
    ------
    BadRequest
        When incoming files are missing or invalid.

    NotFound
        When the dataset does not exist
    """
    if not file_object.file:
        raise BadRequest("No featuretypes part")

    try:
        metadata = stat_dataset(name)
    except FileNotFoundError:
        raise NOT_FOUND

    try:
        ftype_file = file_object.file
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


def read_into_dataframe(file, filename=None, nrows=100, max_characters=50):
    """
    Reads a file into a DataFrame.
    Infers the file encoding and whether a header column exists

    Parameters
    ----------
    file : IO
        File buffer.
    filename : str
        Filename. Used to infer compression. Default to None.
    nrows : int
        Number of rows to peek. Default to 100.
    max_characters : int
        Max characters a column name can have to be distinguished from a real text value. Default to 50.

    Returns
    -------
    pd.DataFrame
        The dataframe content.

    Notes
    -----
    If no filename is given, a hex uuid will be used as the file name.
    """

    detector = UniversalDetector()
    for line, text in enumerate(file):
        detector.feed(text)
        if detector.done or line > nrows:
            break
    detector.close()
    encoding = detector.result.get("encoding")

    if filename is None:
        filename = uuid4().hex

    compression = infer_compression(filename, "infer")

    file.seek(0, SEEK_SET)

    pdread = TextIOWrapper(file, encoding=encoding)
    df0 = pd.read_csv(
        pdread,
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

    file.seek(0, SEEK_SET)
    df = pd.read_csv(
        pdread,
        encoding=encoding,
        compression=compression,
        sep=None,
        engine="python",
        header=header,
        nrows=nrows,
        prefix=prefix,
    )
    return df


def generate_name(filename, attempt=1):
    """Generates a dataset name from a given filename.

    Parameters
    ----------
    filename : str
        Source filename.
    attempt : int
        The current attempt of generating a new name. Default to 1.

    Returns
    -------
    str
        New generated dataset name.
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


def get_featuretypes(name):
    """
    Get the dataset featuretypes.

    Parameters
    ----------
    name : str
        The dataset name to look for in our object storage.

    Returns
    -------
    bytes
        The dataset featuretypes encoded.

    Raises
    ------
    NotFound
        When the dataset does not exist.
    """
    try:
        metadata = stat_dataset(name)
    except FileNotFoundError:
        raise NOT_FOUND

    metadata_featuretypes = metadata.get("featuretypes")
    featuretypes = "\n".join(metadata_featuretypes)
    return featuretypes.encode()
