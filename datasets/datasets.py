from dateutil.parser import parse
from json import dumps, loads
from os import SEEK_SET, SEEK_END, getenv
from os.path import join

import pandas as pd
from minio import Minio
from minio.error import BucketAlreadyOwnedByYou, NoSuchKey
from werkzeug.exceptions import BadRequest, NotFound

client = Minio(
    getenv("MINIO_ENDPOINT"),
    access_key=getenv("MINIO_ACCESS_KEY"),
    secret_key=getenv("MINIO_SECRET_KEY"),
    secure=False,
)

BUCKET = "anonymous"
PREFIX = "datasets"


def list_datasets():
    """Lists all datasets from our object storage.

    Returns:
        A list of all datasets names.
    """
    datasets = []

    # ensures MinIO bucket exists
    make_bucket(BUCKET)

    objects = client.list_objects_v2(BUCKET, PREFIX + "/")
    for obj in objects:
        datasets.append(obj.object_name[len(PREFIX) + 1:])
    return datasets


def create_dataset(files):
    """Creates a new dataset in our object storage.

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

    file_length = get_file_length(file)

    dtypes = infer_dtypes(file)

    # will store columns and featuretypes as metadata
    metadata = {
        "columns": [col for col, _ in dtypes],
        "featuretypes": [dtype for _, dtype in dtypes],
    }

    metadata

    # ensures MinIO bucket exists
    make_bucket(BUCKET)

    # uploads file to MinIO
    # adds the prefix 'datasets/' to the filename
    client.put_object(
        bucket_name=BUCKET,
        object_name=join(PREFIX, file.filename),
        data=file,
        length=file_length,
        metadata=dict((k, dumps(v)) for k, v in metadata.items()),
    )

    # generates a presigned URL for HTTP GET operations
    presigned_url = client.presigned_get_object(
        bucket_name=BUCKET,
        object_name=join(PREFIX, file.filename),
    )
    return {"name": file.filename, "metadata": metadata, "url": presigned_url}


def get_dataset(name):
    """Details a dataset from our object storage.

    Args:
        name: the dataset name to look for in our object storage.

    Returns:
        The dataset info.
    """
    # ensures MinIO bucket exists
    make_bucket(BUCKET)

    try:
        stat = client.stat_object(
            bucket_name=BUCKET,
            object_name=join(PREFIX, name)
        )

        columns = loads(stat.metadata["X-Amz-Meta-Columns"])
        featuretypes = loads(stat.metadata["X-Amz-Meta-Featuretypes"])

        metadata = {
            "columns": columns,
            "featuretypes": featuretypes,
        }

        # generates a presigned URL for HTTP GET operations
        presigned_url = client.presigned_get_object(
            bucket_name=BUCKET,
            object_name=join(PREFIX, name),
        )
        return {"name": name, "metadata": metadata, "url": presigned_url}
    except NoSuchKey:
        raise NotFound("The specified dataset does not exist")


def make_bucket(name):
    """Creates the bucket in MinIO. Ignores exception if bucket already exists.

    Args:
        name: the bucket name
    """
    try:
        client.make_bucket(name)
    except BucketAlreadyOwnedByYou:
        pass


def get_file_length(file):
    """Returns the file length."""
    file.seek(0, SEEK_END)
    file_length = file.tell()
    file.seek(0, SEEK_SET)
    return file_length


def identify_header(file, nrows=5, th=0.9):
    """Analyze whether header should be set to 'infer' or None."""
    df1 = pd.read_csv(file, header="infer", nrows=nrows)
    file.seek(0, SEEK_SET)
    df2 = pd.read_csv(file, header=None, nrows=nrows)
    file.seek(0, SEEK_SET)
    sim = (df1.dtypes.values == df2.dtypes.values).mean()
    return "infer" if sim < th else None


def infer_dtypes(file, nrows=5):
    """Infer data type from DataFrame columns."""
    header = identify_header(file, nrows=nrows)
    dtypes = []
    df = pd.read_csv(file, header=header, prefix="col")
    for col in df.columns:
        if df.dtypes[col].kind == "O":
            if is_datetime(df[col].iloc[:nrows]):
                dtypes.append((str(col), "datetime",))
            else:
                dtypes.append((str(col), "categorical",))
        else:
            dtypes.append((str(col), "numeric",))
    file.seek(0, SEEK_SET)
    return dtypes


def is_datetime(column):
    """Returns whether a column is a DateTime."""
    for _, value in column.iteritems():
        try:
            parse(value)
            break
        except ValueError:
            return False
    return True
