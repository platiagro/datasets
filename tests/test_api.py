import unittest

from minio import Minio
from minio.error import ResponseError

from datasets.api import app
from datasets import datasets


class TestApi(unittest.TestCase):

    def setUp(self):
        # uses public MinIO server
        datasets.client = Minio(
            "play.min.io",
            access_key="Q3AM3UQ867SPQQA43P2F",
            secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
            secure=True,
        )
        try:
            datasets.client.make_bucket(datasets.bucket)
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
