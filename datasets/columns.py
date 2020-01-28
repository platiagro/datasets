from json import loads
from os.path import join

from minio.error import NoSuchKey
from werkzeug.exceptions import NotFound

from .datasets import BUCKET, PREFIX, client, make_bucket


def list_columns(dataset):
    """Lists all columns from a dataset.

    Returns:
        A list of columns names and dtypes.
    """
    columns = []

    # ensures MinIO bucket exists
    make_bucket(BUCKET)

    try:
        stat = client.stat_object(
            bucket_name=BUCKET,
            object_name=join(PREFIX, dataset)
        )
        names = loads(stat.metadata["X-Amz-Meta-Columns"])
        featuretypes = loads(stat.metadata["X-Amz-Meta-Featuretypes"])

        for name, ftype in zip(names, featuretypes):
            columns.append({
                "name": name,
                "featuretype": ftype,
            })

    except NoSuchKey:
        raise NotFound("The specified dataset does not exist")

    return columns
