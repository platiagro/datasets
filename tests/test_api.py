import unittest
from io import BytesIO

from minio import Minio
from minio.error import ResponseError

from datasets.api import app
from datasets.datasets import bucket, client


class TestApi(unittest.TestCase):

    def setUp(self):
        # ensures that the bucket exists and is empty
        try:
            for obj in client.list_objects(bucket, prefix="", recursive=True):
                client.remove_object(bucket, obj.object_name)
        except:
            pass
        try:
            client.make_bucket(bucket)
        except:
            pass

    def test_ping(self):
        with app.test_client() as c:
            rv = c.get("/")
            result = rv.get_data(as_text=True)
            expected = "pong"
            self.assertEqual(result, expected)

    def test_get_datasets(self):
        with app.test_client() as c:
            rv = c.get("/v1/datasets")
            result = rv.get_json()
            expected = []
            self.assertListEqual(result, expected)

    def test_post_datasets(self):
        with app.test_client() as c:
            rv = c.post("/v1/datasets", data={
                "file": (BytesIO(b"5.1,3.5,1.4,0.2,Iris-setosa"), "iris.data"),
            })
            result = rv.get_json()
            expected = {"name": "iris.data"}
            self.assertDictEqual(result, expected)
