import unittest
from io import BytesIO

from minio import Minio
from minio.error import ResponseError

from datasets.api import app
from datasets.datasets import BUCKET, client


class TestApi(unittest.TestCase):

    def setUp(self):
        # ensures that the bucket exists and is empty
        self.empty_bucket()
        self.make_bucket()

    def tearDown(self):
        # removes bucket after the tests complete
        self.empty_bucket()
        self.remove_bucket()

    def empty_bucket(self):
        try:
            for obj in client.list_objects(BUCKET, prefix="", recursive=True):
                client.remove_object(BUCKET, obj.object_name)
        except:
            pass

    def make_bucket(self):
        try:
            client.make_bucket(BUCKET)
        except:
            pass

    def remove_bucket(self):
        try:
            client.remove_bucket(BUCKET)
        except:
            pass

    def test_ping(self):
        with app.test_client() as c:
            rv = c.get("/")
            result = rv.get_data(as_text=True)
            expected = "pong"
            self.assertEqual(result, expected)

    def test_list_datasets(self):
        with app.test_client() as c:
            rv = c.get("/v1/datasets")
            result = rv.get_json()
            expected = []
            self.assertListEqual(result, expected)

    def test_create_dataset(self):
        with app.test_client() as c:
            rv = c.post("/v1/datasets", data={
                "file": (BytesIO(b"01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n" +
                                 b"01/01/2001,4.9,3.0,1.4,0.2,Iris-setosa\n" +
                                 b"01/01/2002,4.7,3.2,1.3,0.2,Iris-setosa\n" +
                                 b"01/01/2003,4.6,3.1,1.5,0.2,Iris-setosa"), "iris.data"),
            })
            result = rv.get_json()
            expected = {
                "name": "iris.data",
                "metadata": {
                    "columns": ["col0", "col1", "col2", "col3", "col4", "col5"],
                    "featuretypes": ["DateTime", "Numerical", "Numerical", "Numerical", "Numerical", "Categorical"],
                },
            }
            if "url" in result:
                del result["url"]
            self.assertDictEqual(expected, result)

    def test_get_dataset(self):
        with app.test_client() as c:
            rv = c.get("/v1/datasets/iris.data")
            result = rv.get_json()
            expected = {"message": "The specified dataset does not exist"}
            self.assertDictEqual(expected, result)

            rv = c.post("/v1/datasets", data={
                "file": (BytesIO(b"01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n" +
                                 b"01/01/2001,4.9,3.0,1.4,0.2,Iris-setosa\n" +
                                 b"01/01/2002,4.7,3.2,1.3,0.2,Iris-setosa\n" +
                                 b"01/01/2003,4.6,3.1,1.5,0.2,Iris-setosa"), "iris.data"),
            })

            rv = c.get("/v1/datasets/iris.data")
            result = rv.get_json()
            expected = {
                "name": "iris.data",
                "metadata": {
                    "columns": ["col0", "col1", "col2", "col3", "col4", "col5"],
                    "featuretypes": ["DateTime", "Numerical", "Numerical", "Numerical", "Numerical", "Categorical"],
                },
            }
            if "url" in result:
                del result["url"]
            self.assertDictEqual(expected, result)

    def test_list_columns(self):
        with app.test_client() as c:
            rv = c.get("/v1/datasets/iris.data/columns")
            result = rv.get_json()
            expected = {"message": "The specified dataset does not exist"}
            self.assertDictEqual(expected, result)

            # adds some data
            rv = c.post("/v1/datasets", data={
                "file": (BytesIO(b"01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n" +
                                 b"01/01/2001,4.9,3.0,1.4,0.2,Iris-setosa\n" +
                                 b"01/01/2002,4.7,3.2,1.3,0.2,Iris-setosa\n" +
                                 b"01/01/2003,4.6,3.1,1.5,0.2,Iris-setosa"), "iris.data"),
            })

            rv = c.get("/v1/datasets/iris.data/columns")
            result = rv.get_json()
            expected = [
                {"name": "col0", "featuretype": "DateTime"},
                {"name": "col1", "featuretype": "Numerical"},
                {"name": "col2", "featuretype": "Numerical"},
                {"name": "col3", "featuretype": "Numerical"},
                {"name": "col4", "featuretype": "Numerical"},
                {"name": "col5", "featuretype": "Categorical"},
            ]
            self.assertListEqual(expected, result)

    def test_update_column(self):
        with app.test_client() as c:
            rv = c.patch("/v1/datasets/iris.data/columns/col0", json={
                "featuretype": "Numerical"
            })
            result = rv.get_json()
            expected = {"message": "The specified dataset does not exist"}
            self.assertDictEqual(expected, result)

            rv = c.post("/v1/datasets", data={
                "file": (BytesIO(b"01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n" +
                                 b"01/01/2001,4.9,3.0,1.4,0.2,Iris-setosa\n" +
                                 b"01/01/2002,4.7,3.2,1.3,0.2,Iris-setosa\n" +
                                 b"01/01/2003,4.6,3.1,1.5,0.2,Iris-setosa"), "iris.data"),
            })

            rv = c.patch("/v1/datasets/iris.data/columns/unk", json={
                "featuretype": "Numerical"
            })
            result = rv.get_json()
            expected = {"message": "The specified column does not exist"}
            self.assertDictEqual(expected, result)

            rv = c.patch("/v1/datasets/iris.data/columns/col0", json={
                "featuretype": "Invalid"
            })
            result = rv.get_json()
            expected = {"message": "featuretype must be one of Numerical, Categorical, DateTime"}
            self.assertDictEqual(expected, result)

            rv = c.patch("/v1/datasets/iris.data/columns/col0", json={
                "featuretype": "Numerical"
            })
            result = rv.get_json()
            expected = {
                "name": "col0",
                "featuretype": "Numerical"
            }
            self.assertDictEqual(expected, result)
