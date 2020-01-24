from os import SEEK_SET, SEEK_END, getenv
from os.path import join

from minio import Minio
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

    file.seek(0, SEEK_END)
    file_length = file.tell()
    file.seek(0, SEEK_SET)

    # TODO saves column types info as metadata
    metadata = {}

    # uploads file to MinIO
    client.put_object(
        bucket_name=bucket,
        object_name=join("datasets", file.filename),
        data=file,
        length=file_length,
        metadata=metadata,
    )
    return {"name": file.filename}
