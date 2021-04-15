# -*- coding: utf-8 -*-
from unittest import TestCase
from fastapi.testclient import TestClient
from datasets.api import app, parse_args

MOCKED_DATASET_PATH = "tests/resources/dataset.csv"
MOCKED_DATASET_PATH_GIF = "tests/resources/image.gif"
MOCKED_DATASET_NO_HEADER_PATH = "tests/resources/iris.data"
MOCKED_DATASET_PATH_TITANIC = "tests/resources/titanic.csv"
MOCKED_DATASET_PATH_FEATURETYPE = "tests/resources/featuretypes.txt"

TEST_CLIENT = TestClient(app)


class TestApi(TestCase):
    maxDiff = None

    def test_parse_args(self):
        parser = parse_args([])
        self.assertEqual(parser.port, 8080)
        self.assertFalse(parser.enable_cors)
        parser = parse_args(["--enable-cors", "--port", "3000"])
        self.assertEqual(parser.port, 3000)
        self.assertTrue(parser.enable_cors)

    def test_ping(self):
        rv = TEST_CLIENT.get("/")
        assert rv.status_code == 200
        assert rv.text == "pong"

    def test_list_datasets(self):
        rv = TEST_CLIENT.get("/datasets")
        result = rv.json()
        self.assertIsInstance(result, list)

    def test_create_datasets(self):
        rv = TEST_CLIENT.post("/datasets", files={
            "file": (
                "dataset.csv",
                open(MOCKED_DATASET_PATH, "rb"),
                "multipart/form-data"
                )
            }
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get("/datasets")
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get("/datasets")
        assert rv.headers["Content-Type"] == "application/json"

        rv = TEST_CLIENT.get("/datasets")
        assert isinstance(rv.json(), list)

        rv = TEST_CLIENT.post("/datasets", files={
            "file": (
                "image.gif",
                open(MOCKED_DATASET_PATH_GIF, "rb"),
                "multipart/form-data"
                )
            }
        )
        result = rv.json()
        expected = {
            "filename": "image.gif"
        }

        self.assertIn("name", result)
        del result["name"]

        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected)
        assert rv.status_code == 200

        rv = TEST_CLIENT.post("/datasets", files={
            "file": (
                "titanic.csv",
                open(MOCKED_DATASET_PATH_TITANIC, "rb"),
                "multipart/form-data"
                )
            }
        )
        result = rv.json()
        expected = {
            "columns": [
                {"featuretype": "Numerical", "name": "PassengerId"},
                {"featuretype": "Numerical", "name": "Survived"},
                {"featuretype": "Numerical", "name": "Pclass"},
                {"featuretype": "Categorical", "name": "Name"},
                {"featuretype": "Categorical", "name": "Sex"},
                {"featuretype": "Numerical", "name": "Age"},
                {"featuretype": "Numerical", "name": "SibSp"},
                {"featuretype": "Numerical", "name": "Parch"},
                {"featuretype": "Categorical", "name": "Ticket"},
                {"featuretype": "Numerical", "name": "Fare"},
                {"featuretype": "Categorical", "name": "Cabin"},
                {"featuretype": "Categorical", "name": "Embarked"},
            ],
            "filename": "titanic.csv",
            "total": 8,
        }
        # name is machine-generated
        # we assert it exists, but we don't assert their values
        self.assertIn("name", result)
        del result["name"]

        # assert that "data" exists, but we don't assert their value
        # since there's nan values
        self.assertIn("data", result)
        del result["data"]

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        # test google file with invalid token
        rv = TEST_CLIENT.post("/datasets", json={
            "gfile": {
                "clientId": "clientId",
                "clientSecret": "clientSecret",
                "id": "id",
                "mimeType": "text/csv",
                "name": "iris.csv",
                "token": "123"
            }
        })
        result = rv.json()
        expected = {'message': 'Invalid token: client unauthorized'}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_get_dataset(self):
        rv = TEST_CLIENT.get("/datasets/UNK")
        result = rv.json()
        expected = {"message": "The specified dataset does not exist"}

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post("/datasets", files={
            "file": (
                "iris.data",
                open(MOCKED_DATASET_NO_HEADER_PATH, "rb"),
                "multipart/form-data"
                )
            }
        )
        name = rv.json().get("name")

        rv = TEST_CLIENT.get(f"/datasets/{name}")
        result = rv.json()

        expected = {
            "columns": [
                {"name": "col0", "featuretype": "DateTime"},
                {"name": "col1", "featuretype": "Numerical"},
                {"name": "col2", "featuretype": "Numerical"},
                {"name": "col3", "featuretype": "Numerical"},
                {"name": "col4", "featuretype": "Numerical"},
                {"name": "col5", "featuretype": "Categorical"},
            ],
            "data": [['01/01/2000', 5.1, 3.5, 1.4, 0.2, 'Iris-setosa'],
                     ['01/01/2001', 4.9, 3.0, 1.4, 0.2, 'Iris-setosa'],
                     ['01/01/2002', 4.7, 3.2, 1.3, 0.2, 'Iris-setosa'],
                     ['01/01/2003', 4.6, 3.1, 1.5, 0.2, 'Iris-setosa']],
            "filename": "iris.data",
            "total": 4
        }

        self.assertIn("name", result)
        del result["name"]

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get(f"/datasets/{name}?page=1&page_size=2")
        result = rv.json()
        expected = {
            "columns": [
                {"name": "col0", "featuretype": "DateTime"},
                {"name": "col1", "featuretype": "Numerical"},
                {"name": "col2", "featuretype": "Numerical"},
                {"name": "col3", "featuretype": "Numerical"},
                {"name": "col4", "featuretype": "Numerical"},
                {"name": "col5", "featuretype": "Categorical"},
            ],
            "data": [['01/01/2000', 5.1, 3.5, 1.4, 0.2, 'Iris-setosa'],
                     ['01/01/2001', 4.9, 3.0, 1.4, 0.2, 'Iris-setosa']],
            "filename": "iris.data",
            "total": 4
        }
        del result["name"]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get(f"/datasets/{name}?page=1&page_size=3")
        result = rv.json()
        expected = {
            "columns": [
                {"name": "col0", "featuretype": "DateTime"},
                {"name": "col1", "featuretype": "Numerical"},
                {"name": "col2", "featuretype": "Numerical"},
                {"name": "col3", "featuretype": "Numerical"},
                {"name": "col4", "featuretype": "Numerical"},
                {"name": "col5", "featuretype": "Categorical"},
            ],
            "data": [['01/01/2000', 5.1, 3.5, 1.4, 0.2, 'Iris-setosa'],
                     ['01/01/2001', 4.9, 3.0, 1.4, 0.2, 'Iris-setosa'],
                     ['01/01/2002', 4.7, 3.2, 1.3, 0.2, 'Iris-setosa']],
            "filename": "iris.data",
            "total": 4
        }
        del result["name"]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get("/datasets/iris.data?page=15&page_size=2")
        result = rv.json()
        expected = {"message": "The specified page does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/datasets/{name}?page=A&page_size=2")
        result = rv.json()
        expected = {
            "detail": [
                    {
                        "loc": [
                            "query",
                            "page"
                        ],
                        "msg": "value is not a valid integer",
                        "type": "type_error.integer"
                    }
            ]
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 422)

        rv = TEST_CLIENT.get(f"/datasets/iris.data?page_size=-1")
        result = rv.json()
        expected = {
            "columns": [
                {"name": "col0", "featuretype": "DateTime"},
                {"name": "col1", "featuretype": "Numerical"},
                {"name": "col2", "featuretype": "Numerical"},
                {"name": "col3", "featuretype": "Numerical"},
                {"name": "col4", "featuretype": "Numerical"},
                {"name": "col5", "featuretype": "Categorical"},
            ],
            "data": [['01/01/2000', 5.1, 3.5, 1.4, 0.2, 'Iris-setosa'],
                     ['01/01/2001', 4.9, 3.0, 1.4, 0.2, 'Iris-setosa'],
                     ['01/01/2002', 4.7, 3.2, 1.3, 0.2, 'Iris-setosa'],
                     ['01/01/2003', 4.6, 3.1, 1.5, 0.2, 'Iris-setosa']],
            "filename": "iris.data",
            "total": 4
        }
        # name is machine-generated
        # we assert it exists, but we don't check its value
        self.assertIn("name", result)
        del result["name"]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.get(f"/datasets/iris.data?page_size=-2")
        result = rv.json()
        expected = {
            "columns": [
                {"name": "col0", "featuretype": "DateTime"},
                {"name": "col1", "featuretype": "Numerical"},
                {"name": "col2", "featuretype": "Numerical"},
                {"name": "col3", "featuretype": "Numerical"},
                {"name": "col4", "featuretype": "Numerical"},
                {"name": "col5", "featuretype": "Categorical"},
            ],
            "data": [['01/01/2000', 5.1, 3.5, 1.4, 0.2, 'Iris-setosa'],
                     ['01/01/2001', 4.9, 3.0, 1.4, 0.2, 'Iris-setosa']],
            "filename": "iris.data",
            "total": 4
        }
        # name is machine-generated
        # we assert it exists, but we don't check its value
        self.assertIn("name", result)
        del result["name"]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_list_columns(self):
        rv = TEST_CLIENT.get("/datasets/UNK/columns")

        result = rv.json()
        expected = {"message": "The specified dataset does not exist"}

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post("/datasets", files={
            "file": (
                "iris.data",
                open(MOCKED_DATASET_NO_HEADER_PATH, "rb"),
                "multipart/form-data"
                )
            }
        )
        name = rv.json().get("name")

        rv = TEST_CLIENT.get(f"/datasets/{name}/columns")
        result = rv.json()
        expected = [
            {"name": "col0", "featuretype": "DateTime"},
            {"name": "col1", "featuretype": "Numerical"},
            {"name": "col2", "featuretype": "Numerical"},
            {"name": "col3", "featuretype": "Numerical"},
            {"name": "col4", "featuretype": "Numerical"},
            {"name": "col5", "featuretype": "Categorical"},
        ]

        self.assertListEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_update_column(self):
        rv = TEST_CLIENT.patch("/datasets/UNK/columns/col0", json={"featuretype": "Numerical"})
        result = rv.json()
        expected = {"message": "The specified dataset does not exist"}

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post("/datasets", files={
            "file": (
                "iris.data",
                open(MOCKED_DATASET_NO_HEADER_PATH, "rb"),
                "multipart/form-data"
                )
            }
        )
        name = rv.json().get("name")

        rv = TEST_CLIENT.patch(f"/datasets/{name}/columns/unk", json={"featuretype": "Numerical"})
        result = rv.json()
        expected = {"message": "The specified column does not exist"}

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/datasets/{name}/columns/col0", json={"featuretype": "Invalid"})
        result = rv.json()
        expected = {"message": "featuretype must be one of DateTime, Numerical, Categorical"}

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.patch(f"/datasets/{name}/columns/col0", json={"featuretype": "Numerical"})
        result = rv.json()
        expected = {
            "name": "col0",
            "featuretype": "Numerical"
        }

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.post("/datasets", files={
            "file": (
                "image.gif",
                open(MOCKED_DATASET_PATH_GIF, "rb"),
                "multipart/form-data"
                )
            }
        )
        name = rv.json().get("name")

        rv = TEST_CLIENT.patch(f"/datasets/{name}/columns/unk", json={"featuretype": "Numerical"})

        result = rv.json()
        expected = {"message": "The specified column does not exist"}

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_patch_dataset(self):
        rv = TEST_CLIENT.patch("/datasets/UNK", files={
            "featuretypes": (
                "featuretypes.txt",
                open(MOCKED_DATASET_PATH_FEATURETYPE, "rb"),
                "multipart/form-data"
            )
            }
        )
        result = rv.json()
        expected = {"message": "The specified dataset does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post("/datasets", files={
            "file": (
                "iris.data",
                open(MOCKED_DATASET_NO_HEADER_PATH, "rb"),
                "multipart/form-data"
                )
            }
        )
        name = rv.json().get("name")

        rv = TEST_CLIENT.patch(f"/datasets/{name}", files={
            "featuretypes": (
                "featuretypes.txt",
                open(MOCKED_DATASET_PATH_FEATURETYPE, "rb"),
                "multipart/form-data"
            )
            }
        )
        result = rv.json()
        expected = {
                "columns": [
                    {"name": "col0", "featuretype": "DateTime"},
                    {"name": "col1", "featuretype": "Numerical"},
                    {"name": "col2", "featuretype": "Numerical"},
                    {"name": "col3", "featuretype": "Numerical"},
                    {"name": "col4", "featuretype": "Numerical"},
                    {"name": "col5", "featuretype": "Categorical"},
                ],
                "data": [['01/01/2000', 5.1, 3.5, 1.4, 0.2, 'Iris-setosa'],
                         ['01/01/2001', 4.9, 3.0, 1.4, 0.2, 'Iris-setosa'],
                         ['01/01/2002', 4.7, 3.2, 1.3, 0.2, 'Iris-setosa'],
                         ['01/01/2003', 4.6, 3.1, 1.5, 0.2, 'Iris-setosa']],
                "filename": "iris.data",
                "name": name,
                "total": 4
            }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_get_dataset_featuretypes(self):
        rv = TEST_CLIENT.get("/datasets/UNK/featuretypes")
        result = rv.json()
        expected = {"message": "The specified dataset does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post("/datasets", files={
            "file": (
                "iris.data",
                open(MOCKED_DATASET_NO_HEADER_PATH, "rb"),
                "multipart/form-data"
                )
            }
        )
        name = rv.json().get("name")

        rv = TEST_CLIENT.get(f"/datasets/{name}/featuretypes")
        result = rv.text
        expected = b'DateTime\nNumerical\nNumerical\nNumerical\nNumerical\nCategorical'
        self.assertEqual(expected, expected)
        self.assertEqual(rv.status_code, 200)
