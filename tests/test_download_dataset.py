# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from datasets.api import app

import tests.util as util

TEST_CLIENT = TestClient(app)


class TestDownloadDataset(unittest.TestCase):
    @mock.patch(
        "platiagro.get_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    def test_download_dataset_not_found(self, mock_get_dataset):
        """
        Should raise http status 404 when given name does not exist.
        """
        dataset_name = "UNK"

        rv = TEST_CLIENT.get(f"/datasets/{dataset_name}/downloads")
        result = rv.json()
        expected = {"message": "The specified dataset does not exist"}

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)
        mock_get_dataset.assert_any_call(dataset_name)

    @mock.patch(
        "platiagro.get_dataset",
        side_effect=util.get_dataset_side_effect,
    )
    def test_download_dataset_iris_csv_success(self, mock_get_dataset):
        """
        Should return iris dataset contents successfully.
        """
        dataset_name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.get(f"/datasets/{dataset_name}/downloads")
        result = rv.text

        expected = util.IRIS_DATA
        self.assertEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers["content-type"], "text/csv")
        mock_get_dataset.assert_any_call(dataset_name)

    @mock.patch(
        "platiagro.get_dataset",
        side_effect=util.get_dataset_side_effect,
    )
    def test_download_dataset_png_success(self, mock_get_dataset):
        """
        Should return PNG dataset contents successfully.
        """
        dataset_name = util.PNG_DATASET_NAME

        rv = TEST_CLIENT.get(f"/datasets/{dataset_name}/downloads")
        result = rv.content

        expected = util.PNG_DATA
        self.assertEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers["content-type"], "image/png")
        mock_get_dataset.assert_any_call(dataset_name)
