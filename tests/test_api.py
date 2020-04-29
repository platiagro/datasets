# -*- coding: utf-8 -*-
from io import BytesIO
from unittest import TestCase

from datasets.api import app, parse_args


class TestApi(TestCase):

    def iris_file(self):
        return (BytesIO(b"01/01/2000,5.1,3.5,1.4,0.2,Iris-setosa\n" +
                        b"01/01/2001,4.9,3.0,1.4,0.2,Iris-setosa\n" +
                        b"01/01/2002,4.7,3.2,1.3,0.2,Iris-setosa\n" +
                        b"01/01/2003,4.6,3.1,1.5,0.2,Iris-setosa"), "iris.data",)

    def iris_featuretypes(self):
        return (BytesIO(b"DateTime\n" +
                        b"Numerical\n" +
                        b"Numerical\n" +
                        b"Numerical\n" +
                        b"Numerical\n" +
                        b"Categorical"), "featuretypes.txt",)

    def boston_file(self):
        return (BytesIO(b"0.00632	18	2.31	0	0.538	6.575	65.2	4.09	1	296	15.3	396.9	4.98	24\n" +
                        b"0.02731	0	7.07	0	0.469	6.421	78.9	4.9671	2	242	17.8	396.9	9.14	21.6\n" +
                        b"0.02729	0	7.07	0	0.469	7.185	61.1	4.9671	2	242	17.8	392.83	4.03	34.7\n" +
                        b"0.03237	0	2.18	0	0.458	6.998	45.8	6.0622	3	222	18.7	394.63	2.94	33.4\n" +
                        b"0.06905	0	2.18	0	0.458	7.147	54.2	6.0622	3	222	18.7	396.9	5.33	36.2"), "boston.data",)

    def test_parse_args(self):
        parser = parse_args([])
        self.assertEqual(parser.port, 8080)
        self.assertFalse(parser.enable_cors)

        parser = parse_args(["--enable-cors", "--port", "3000"])
        self.assertEqual(parser.port, 3000)
        self.assertTrue(parser.enable_cors)

    def test_ping(self):
        with app.test_client() as c:
            rv = c.get("/")
            result = rv.get_data(as_text=True)
            expected = "pong"
            self.assertEqual(result, expected)

    def test_list_datasets(self):
        with app.test_client() as c:
            rv = c.get("/datasets")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_dataset(self):
        with app.test_client() as c:
            rv = c.post("/datasets", data={})
            result = rv.get_json()
            expected = {"message": "No file part"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/datasets", data={"file": (BytesIO(), "")})
            result = rv.get_json()
            expected = {"message": "No selected file"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/datasets", data={
                "file": self.iris_file(),
                "featuretypes": (BytesIO(b"date\n" +
                                         b"float\n" +
                                         b"float\n" +
                                         b"float\n" +
                                         b"float\n" +
                                         b"string"), "featuretypes.txt"),
            })
            result = rv.get_json()
            expected = {
                "message": "featuretype must be one of DateTime, Numerical, Categorical"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/datasets", data={
                "file": self.iris_file(),
                "featuretypes": (BytesIO(b"DateTime"), "featuretypes.txt"),
            })
            result = rv.get_json()
            expected = {
                "message": "featuretypes must be the same length as the DataFrame columns"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/datasets", data={
                "file": self.iris_file(),
            })
            result = rv.get_json()
            expected = {
                "columns": [
                    {"name": "col0", "featuretype": "DateTime"},
                    {"name": "col1", "featuretype": "Numerical"},
                    {"name": "col2", "featuretype": "Numerical"},
                    {"name": "col3", "featuretype": "Numerical"},
                    {"name": "col4", "featuretype": "Numerical"},
                    {"name": "col5", "featuretype": "Categorical"},
                ],
                "filename": "iris.data",
            }
            # name is machine-generated
            # we assert it exists, but we don't assert their values
            self.assertIn("name", result)
            del result["name"]
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 200)

            rv = c.post("/datasets", data={
                "file": self.boston_file(),
            })
            result = rv.get_json()
            expected = {
                "columns": [
                    {"name": "col0", "featuretype": "Numerical"},
                    {"name": "col1", "featuretype": "Numerical"},
                    {"name": "col2", "featuretype": "Numerical"},
                    {"name": "col3", "featuretype": "Numerical"},
                    {"name": "col4", "featuretype": "Numerical"},
                    {"name": "col5", "featuretype": "Numerical"},
                    {"name": "col6", "featuretype": "Numerical"},
                    {"name": "col7", "featuretype": "Numerical"},
                    {"name": "col8", "featuretype": "Numerical"},
                    {"name": "col9", "featuretype": "Numerical"},
                    {"name": "col10", "featuretype": "Numerical"},
                    {"name": "col11", "featuretype": "Numerical"},
                    {"name": "col12", "featuretype": "Numerical"},
                    {"name": "col13", "featuretype": "Numerical"},
                ],
                "filename": "boston.data",
            }
            # name is machine-generated
            # we assert it exists, but we don't assert their values
            self.assertIn("name", result)
            del result["name"]
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 200)

            rv = c.post("/datasets", data={
                "file": self.iris_file(),
                "featuretypes": self.iris_featuretypes(),
            })
            result = rv.get_json()
            expected = {
                "columns": [
                    {"name": "col0", "featuretype": "DateTime"},
                    {"name": "col1", "featuretype": "Numerical"},
                    {"name": "col2", "featuretype": "Numerical"},
                    {"name": "col3", "featuretype": "Numerical"},
                    {"name": "col4", "featuretype": "Numerical"},
                    {"name": "col5", "featuretype": "Categorical"},
                ],
                "filename": "iris.data",
            }
            self.assertIn("name", result)
            del result["name"]
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 200)

    def test_get_dataset(self):
        with app.test_client() as c:
            rv = c.get("/datasets/iris.data")
            result = rv.get_json()
            expected = {"message": "The specified dataset does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post("/datasets", data={
                "file": self.iris_file(),
            })
            name = rv.get_json().get("name")

            rv = c.get("/datasets/{}".format(name))
            result = rv.get_json()
            expected = {
                "columns": [
                    {"name": "col0", "featuretype": "DateTime"},
                    {"name": "col1", "featuretype": "Numerical"},
                    {"name": "col2", "featuretype": "Numerical"},
                    {"name": "col3", "featuretype": "Numerical"},
                    {"name": "col4", "featuretype": "Numerical"},
                    {"name": "col5", "featuretype": "Categorical"},
                ],
                "filename": "iris.data",
            }
            # name is machine-generated
            # we assert it exists, but we don't check its value
            self.assertIn("name", result)
            del result["name"]
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 200)

    def test_list_columns(self):
        with app.test_client() as c:
            rv = c.get("/datasets/iris.data/columns")
            result = rv.get_json()
            expected = {"message": "The specified dataset does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post("/datasets", data={
                "file": self.iris_file(),
            })
            name = rv.get_json().get("name")

            rv = c.get("/datasets/{}/columns".format(name))
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
            self.assertEqual(rv.status_code, 200)

    def test_update_column(self):
        with app.test_client() as c:
            rv = c.patch("/datasets/iris.data/columns/col0", json={
                "featuretype": "Numerical"
            })
            result = rv.get_json()
            expected = {"message": "The specified dataset does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post("/datasets", data={
                "file": self.iris_file(),
            })
            name = rv.get_json().get("name")

            rv = c.patch("/datasets/{}/columns/unk".format(name), json={
                "featuretype": "Numerical"
            })
            result = rv.get_json()
            expected = {"message": "The specified column does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch("/datasets/{}/columns/col0".format(name), json={
                "featuretype": "Invalid"
            })
            result = rv.get_json()
            expected = {
                "message": "featuretype must be one of DateTime, Numerical, Categorical"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.patch("/datasets/{}/columns/col0".format(name), json={
                "featuretype": "Numerical"
            })
            result = rv.get_json()
            expected = {
                "name": "col0",
                "featuretype": "Numerical"
            }
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 200)
