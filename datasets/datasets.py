from os import SEEK_SET, SEEK_END, getenv
from os.path import join

import pandas as pd
from minio import Minio
from minio.error import BucketAlreadyOwnedByYou
from werkzeug.exceptions import BadRequest

client = Minio(
    getenv("MINIO_ENDPOINT"),
    access_key=getenv("MINIO_ACCESS_KEY"),
    secret_key=getenv("MINIO_SECRET_KEY"),
    secure=False,
)

bucket = "anonymous"


def list_datasets():
    """Lists all datasets from our object storage.

    Returns:
        A list of all datasets names.
    """
    datasets = []

    # ensures MinIO bucket exists
    make_bucket()

    objects = client.list_objects_v2(bucket, "datasets/")
    for obj in objects:
        datasets.append(obj.object_name.encode("utf-8"))
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

    # will store data types as metadata
    metadata = dict((col, dtype) for col, dtype in dtypes)

    # ensures MinIO bucket exists
    make_bucket()

    # uploads file to MinIO
    # adds the prefix 'datasets/' to the filename
    client.put_object(
        bucket_name=bucket,
        object_name=join("datasets", file.filename),
        data=file,
        length=file_length,
        metadata=metadata,
    )

    # generates a presigned URL for HTTP GET operations
    presigned_url = client.presigned_get_object(
        bucket_name=bucket,
        object_name=join("datasets", file.filename),
    )
    return {"name": file.filename, "metadata": metadata, "url": presigned_url}


def make_bucket():
    """Creates the bucket in MinIO."""
    try:
        client.make_bucket(bucket)
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
            dtypes.append((str(col), "category",))
        else:
            dtypes.append((str(col), "numeric",))
    file.seek(0, SEEK_SET)
    return dtypes
