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

    def mock_file(self):
        return (BytesIO(b"01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n" +
                        b"01/01/2001,4.9,3.0,1.4,0.2,Iris-setosa\n" +
                        b"01/01/2002,4.7,3.2,1.3,0.2,Iris-setosa\n" +
                        b"01/01/2003,4.6,3.1,1.5,0.2,Iris-setosa"), "iris.data",)

    def mock_featuretypes(self):
        return (BytesIO(b"DateTime\n" +
                        b"Numerical\n" +
                        b"Numerical\n" +
                        b"Numerical\n" +
                        b"Numerical\n" +
                        b"Categorical"), "featuretypes.txt",)

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

            rv = c.post("/v1/datasets", data={
                "file": self.mock_file(),
            })

            rv = c.get("/v1/datasets")
            result = rv.get_json()
            for r in result:
                self.assertIn("name", r)
                del r["name"]

            expected = [{"filename": "iris.data"}]
            self.assertListEqual(result, expected)

    def test_create_dataset(self):
        with app.test_client() as c:
            rv = c.post("/v1/datasets", data={})
            result = rv.get_json()
            expected = {"message": "No file part"}
            self.assertDictEqual(expected, result)

            rv = c.post("/v1/datasets", data={"file": (BytesIO(), "")})
            result = rv.get_json()
            expected = {"message": "No selected file"}
            self.assertDictEqual(expected, result)

            rv = c.post("/v1/datasets", data={
                "file": self.mock_file(),
                "featuretypes": (BytesIO(b"date\n" +
                                         b"float\n" +
                                         b"float\n" +
                                         b"float\n" +
                                         b"float\n" +
                                         b"string"), "featuretypes.txt"),
            })
            result = rv.get_json()
            expected = {
                "message": "featuretypes must be one of Numerical, Categorical, DateTime"}

            rv = c.post("/v1/datasets", data={
                "file": self.mock_file(),
                "featuretypes": (BytesIO(b"DateTime"), "featuretypes.txt"),
            })
            result = rv.get_json()
            expected = {
                "message": "featuretypes must be the same length as columns"}

            rv = c.post("/v1/datasets", data={
                "file": self.mock_file(),
            })
            result = rv.get_json()
            expected = {
                "filename": "iris.data",
                "columns": [
                    {"name": "col0", "featuretype": "DateTime"},
                    {"name": "col1", "featuretype": "Numerical"},
                    {"name": "col2", "featuretype": "Numerical"},
                    {"name": "col3", "featuretype": "Numerical"},
                    {"name": "col4", "featuretype": "Numerical"},
                    {"name": "col5", "featuretype": "Categorical"},
                ],
            }
            # name and url are machine-generated
            # we assert they exist, but we don't their values
            self.assertIn("name", result)
            del result["name"]
            self.assertIn("url", result)
            del result["url"]
            self.assertDictEqual(expected, result)

            rv = c.post("/v1/datasets", data={
                "file": self.mock_file(),
                "featuretypes": self.mock_featuretypes(),
            })
            result = rv.get_json()
            expected = {
                "filename": "iris.data",
                "columns": [
                    {"name": "col0", "featuretype": "DateTime"},
                    {"name": "col1", "featuretype": "Numerical"},
                    {"name": "col2", "featuretype": "Numerical"},
                    {"name": "col3", "featuretype": "Numerical"},
                    {"name": "col4", "featuretype": "Numerical"},
                    {"name": "col5", "featuretype": "Categorical"},
                ],
            }
            self.assertIn("name", result)
            del result["name"]
            self.assertIn("url", result)
            del result["url"]
            self.assertDictEqual(expected, result)

    def test_get_dataset(self):
        with app.test_client() as c:
            rv = c.get("/v1/datasets/iris.data")
            result = rv.get_json()
            expected = {"message": "The specified dataset does not exist"}
            self.assertDictEqual(expected, result)

            rv = c.post("/v1/datasets", data={
                "file": self.mock_file(),
            })
            name = rv.get_json().get("name")

            rv = c.get("/v1/datasets/{}".format(name))
            result = rv.get_json()
            expected = {
                "filename": "iris.data",
                "columns": [
                    {"name": "col0", "featuretype": "DateTime"},
                    {"name": "col1", "featuretype": "Numerical"},
                    {"name": "col2", "featuretype": "Numerical"},
                    {"name": "col3", "featuretype": "Numerical"},
                    {"name": "col4", "featuretype": "Numerical"},
                    {"name": "col5", "featuretype": "Categorical"},
                ],
            }
            # name and url are machine-generated
            # we assert they exist, but we don't their values
            self.assertIn("name", result)
            del result["name"]
            self.assertIn("url", result)
            del result["url"]
            self.assertDictEqual(expected, result)

    def test_list_columns(self):
        with app.test_client() as c:
            rv = c.get("/v1/datasets/iris.data/columns")
            result = rv.get_json()
            expected = {"message": "The specified dataset does not exist"}
            self.assertDictEqual(expected, result)

            rv = c.post("/v1/datasets", data={
                "file": self.mock_file(),
            })
            name = rv.get_json().get("name")

            rv = c.get("/v1/datasets/{}/columns".format(name))
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
                "file": self.mock_file(),
            })
            name = rv.get_json().get("name")

            rv = c.patch("/v1/datasets/{}/columns/unk".format(name), json={
                "featuretype": "Numerical"
            })
            result = rv.get_json()
            expected = {"message": "The specified column does not exist"}
            self.assertDictEqual(expected, result)

            rv = c.patch("/v1/datasets/{}/columns/col0".format(name), json={
                "featuretype": "Invalid"
            })
            result = rv.get_json()
            expected = {
                "message": "featuretype must be one of Numerical, Categorical, DateTime"}
            self.assertDictEqual(expected, result)

            rv = c.patch("/v1/datasets/{}/columns/col0".format(name), json={
                "featuretype": "Numerical"
            })
            result = rv.get_json()
            expected = {
                "name": "col0",
                "featuretype": "Numerical"
            }
            self.assertDictEqual(expected, result)
