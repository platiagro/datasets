from os import getenv

from minio import Minio

client = Minio(
    getenv("MINIO_ENDPOINT"),
    access_key=getenv("MINIO_ACCESS_KEY"),
    secret_key=getenv("MINIO_SECRET_KEY"),
    secure=False,
)

bucket = "mlpipeline"


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
