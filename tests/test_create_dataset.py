# -*- coding: utf-8 -*-
import io
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from datasets.api import app

import tests.util as util

TEST_CLIENT = TestClient(app)


class TestCreateDataset(unittest.TestCase):
    maxDiff = None

    @mock.patch(
        "datasets.datasets.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    @mock.patch(
        "datasets.datasets.save_dataset",
    )
    def test_create_dataset_with_iris_csv(self, mock_save_dataset, mock_stat_dataset):
        """
        Should call platiagro.save_dataset using given file, filename, and metadata
        (columns, featurestypes, total, original-filename).
        """
        dataset_name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.post(
            "/datasets",
            files={
                "file": (
                    dataset_name,
                    io.StringIO(util.IRIS_DATA),
                    "multipart/form-data",
                )
            },
        )
        result = rv.json()

        expected = {
            "name": dataset_name,
            "filename": dataset_name,
            "total": len(util.IRIS_DATA_ARRAY),
            "columns": util.IRIS_COLUMNS_FEATURETYPES,
            "data": util.IRIS_DATA_ARRAY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)
        mock_stat_dataset.assert_any_call(dataset_name)
        mock_save_dataset.assert_any_call(
            dataset_name,
            mock.ANY,
            metadata={
                "columns": util.IRIS_COLUMNS,
                "featuretypes": util.IRIS_FEATURETYPES,
                "original-filename": util.IRIS_DATASET_NAME,
                "total": len(util.IRIS_DATA_ARRAY),
            },
        )

    @mock.patch(
        "datasets.datasets.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    @mock.patch(
        "datasets.datasets.save_dataset",
    )
    def test_create_dataset_with_iris_csv_headerless(
        self, mock_save_dataset, mock_stat_dataset
    ):
        """
        Should call platiagro.save_dataset using given file, filename, and metadata (columns, featurestypes, total, original-filename).
        """
        dataset_name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.post(
            "/datasets",
            files={
                "file": (
                    dataset_name,
                    io.StringIO(util.IRIS_DATA_HEADERLESS),
                    "multipart/form-data",
                )
            },
        )
        result = rv.json()

        expected = {
            "name": dataset_name,
            "filename": dataset_name,
            "total": len(util.IRIS_DATA_ARRAY),
            "columns": util.IRIS_HEADERLESS_COLUMNS_FEATURETYPES,
            "data": util.IRIS_DATA_ARRAY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)
        mock_stat_dataset.assert_any_call(dataset_name)
        mock_save_dataset.assert_any_call(
            dataset_name,
            mock.ANY,
            metadata={
                "columns": util.IRIS_HEADERLESS_COLUMNS,
                "featuretypes": util.IRIS_FEATURETYPES,
                "original-filename": util.IRIS_DATASET_NAME,
                "total": len(util.IRIS_DATA_ARRAY),
            },
        )

    @mock.patch(
        "datasets.datasets.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    @mock.patch(
        "datasets.datasets.save_dataset",
    )
    def test_create_dataset_with_png(self, mock_save_dataset, mock_stat_dataset):
        """
        Should call platiagro.save_dataset using given file, filename, and metadata (original-filename).
        """
        dataset_name = util.PNG_DATASET_NAME

        rv = TEST_CLIENT.post(
            "/datasets",
            files={
                "file": (
                    dataset_name,
                    io.BytesIO(util.PNG_DATA),
                    "multipart/form-data",
                )
            },
        )
        result = rv.json()

        expected = {
            "name": dataset_name,
            "filename": dataset_name,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)
        mock_stat_dataset.assert_any_call(dataset_name)
        mock_save_dataset.assert_any_call(
            dataset_name,
            mock.ANY,
            metadata={
                "original-filename": util.PNG_DATASET_NAME,
            },
        )

    def test_create_dataset_with_gfile_client_unauthorized(self):
        """
        Should raise http status 400 client unauthorized when given clientId and clientSecret are invalid.
        """
        rv = TEST_CLIENT.post(
            "/datasets",
            json={
                "gfile": {
                    "clientId": "clientId",
                    "clientSecret": "clientSecret",
                    "id": "id",
                    "mimeType": "text/csv",
                    "name": "iris.csv",
                    "token": "123",
                }
            },
        )
        result = rv.json()

        expected = {
            "message": "Invalid token: client unauthorized",
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

    @mock.patch(
        "datasets.datasets.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    @mock.patch(
        "datasets.datasets.save_dataset",
    )
    def test_create_dataset_with_predict_file_csv(self, mock_save_dataset, mock_stat_dataset):
        """
        Should call platiagro.save_dataset using given file, filename, and metadata (columns, featurestypes, total, original-filename).
        """
        dataset_name = util.PREDICT_FILE

        rv = TEST_CLIENT.post(
            "/datasets",
            files={
                "file": (
                    dataset_name,
                    util.PREDICT_FILE_HEADER,
                    "multipart/form-data",
                )
            },
        )
        result = rv.json()

        expected = {
            "name": dataset_name,
            "filename": dataset_name,
            "total": len(util.PREDICT_FILE_DATA),
            "columns": util.PREDICT_FILE_COLUMNS,
            "data": util.PREDICT_FILE_DATA,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)
        mock_stat_dataset.assert_any_call(dataset_name)
        mock_save_dataset.assert_any_call(
            dataset_name,
            mock.ANY,
            metadata={
                "columns": util.PREDICT_COLUMNS,
                "featuretypes": util.PREDICT_FEATURETYPES,
                "original-filename": util.PREDICT_FILE,
                "total": len(util.PREDICT_FILE_DATA),
            },
        )

    @mock.patch(
        "datasets.datasets.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    @mock.patch(
        "datasets.datasets.save_dataset",
    )
    def test_create_dataset_with_predict_file_headerless_csv(self, mock_save_dataset, mock_stat_dataset):
        """
        Should call platiagro.save_dataset using given file, filename, and metadata (columns, featurestypes, total, original-filename).
        """
        dataset_name = util.PREDICT_HEADERLESS

        rv = TEST_CLIENT.post(
            "/datasets",
            files={
                "file": (
                    dataset_name,
                    util.PREDICT_FILE_HEADERLESS,
                    "multipart/form-data",
                )
            },
        )
        result = rv.json()

        expected = {
            "name": dataset_name,
            "filename": dataset_name,
            "total": len(util.PREDICT_FILE_DATA),
            "columns": util.PREDICT_FILE_COLUMNS_HEADERLESS,
            "data": util.PREDICT_FILE_DATA,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)
        mock_stat_dataset.assert_any_call(dataset_name)
        mock_save_dataset.assert_any_call(
            dataset_name,
            mock.ANY,
            metadata={
                "columns": util.PREDICT_COLUMNS_HEADERLESS,
                "featuretypes": util.PREDICT_FEATURETYPES,
                "original-filename": util.PREDICT_HEADERLESS,
                "total": len(util.PREDICT_FILE_DATA),
            },
        )
