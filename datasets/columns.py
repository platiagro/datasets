from json import loads, dumps
from os.path import join

from minio.error import NoSuchKey
from werkzeug.exceptions import BadRequest, NotFound

from .datasets import BUCKET, PREFIX, client, make_bucket


def list_columns(dataset):
    """Lists all columns from a dataset.

    Args:
        dataset: the dataset name.

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


def update_column(dataset, column, featuretype):
    """Updates a column from a dataset.

    Args:
        dataset: the dataset name.
        column: the column name.
        featuretype: the feature type (Numerical, Categorical, or DateTime).

    Returns:
        The column info.
    """

    # ensures MinIO bucket exists
    make_bucket(BUCKET)

    try:
        # there aren't any methods that updates metadata only,
        # so the only possible solution is to download the file,
        # then reupload it, and pass the new metadata

        # downloads file from MinIO
        data = client.get_object(
            bucket_name=BUCKET,
            object_name=join(PREFIX, dataset),
        )

        # gets the metadata
        stat = client.stat_object(
            bucket_name=BUCKET,
            object_name=join(PREFIX, dataset)
        )
        columns = loads(stat.metadata["X-Amz-Meta-Columns"])
        featuretypes = loads(stat.metadata["X-Amz-Meta-Featuretypes"])

        # sets new metadata
        idx = columns.index(column)
        featuretypes[idx] = featuretype
        metadata = {
            "columns": columns,
            "featuretypes": featuretypes,
        }

        if featuretype not in ["Numerical", "Categorical", "DateTime"]:
            raise BadRequest("featuretype must be one of Numerical, Categorical, DateTime")

        # reuploads file to MinIO, passing the new metadata
        client.put_object(
            bucket_name=BUCKET,
            object_name=join(PREFIX, dataset),
            data=data,
            length=int(data.headers["Content-Length"]),
            metadata=dict((k, dumps(v)) for k, v in metadata.items()),
        )

    except NoSuchKey:
        raise NotFound("The specified dataset does not exist")
    except ValueError:
        raise NotFound("The specified column does not exist")

    return {"name": column, "featuretype": featuretype}
