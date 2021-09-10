# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from datasets.api import app

import tests.util as util

TEST_CLIENT = TestClient(app)


class TestGetDataset(unittest.TestCase):
    @mock.patch(
        "datasets.datasets.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    def test_get_dataset_not_found(self, mock_stat_dataset):
        """
        Should raise http status 404 when given name does not exist.
        """
        dataset_name = "UNK"

        rv = TEST_CLIENT.get(f"/datasets/{dataset_name}")
        result = rv.json()
        expected = {"message": "The specified dataset does not exist"}

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)
        mock_stat_dataset.assert_any_call(dataset_name)

    @mock.patch(
        "datasets.datasets.stat_dataset",
        return_value={
            "columns": util.IRIS_COLUMNS,
            "featuretypes": util.IRIS_FEATURETYPES,
            "original-filename": util.IRIS_DATASET_NAME,
            "total": len(util.IRIS_DATA_ARRAY),
        },
    )
    @mock.patch(
        "datasets.datasets.load_dataset",
        return_value=util.IRIS_DATAFRAME,
    )
    def test_get_dataset_iris_csv_success(self, mock_load_dataset, mock_stat_dataset):
        """
        Should return dataset contents successfully.
        """
        dataset_name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.get(f"/datasets/{dataset_name}")
        result = rv.json()

        expected = {
            "columns": util.IRIS_COLUMNS_FEATURETYPES,
            "data": util.IRIS_DATA_ARRAY,
            "filename": util.IRIS_DATASET_NAME,
            "name": util.IRIS_DATASET_NAME,
            "total": len(util.IRIS_DATA_ARRAY),
        }
        self.assertEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
        mock_stat_dataset.assert_any_call(dataset_name)
        mock_load_dataset.assert_any_call(dataset_name)

    @mock.patch(
        "datasets.datasets.stat_dataset",
        return_value={
            "columns": util.IRIS_COLUMNS,
            "featuretypes": util.IRIS_FEATURETYPES,
            "original-filename": util.IRIS_DATASET_NAME,
            "total": len(util.IRIS_DATA_ARRAY),
        },
    )
    @mock.patch(
        "datasets.datasets.load_dataset",
        return_value=util.IRIS_DATAFRAME,
    )
    def test_get_dataset_iris_csv_with_page_size_2_and_page_1(
        self, mock_load_dataset, mock_stat_dataset
    ):
        """
        Should return the 1st page of size 2 from dataset contents.
        """
        dataset_name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.get(f"/datasets/{dataset_name}?page=1&page_size=2")
        result = rv.json()

        expected = {
            "columns": util.IRIS_COLUMNS_FEATURETYPES,
            "data": util.IRIS_DATA_ARRAY[:2],
            "filename": util.IRIS_DATASET_NAME,
            "name": util.IRIS_DATASET_NAME,
            "total": len(util.IRIS_DATA_ARRAY),
        }
        self.assertEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
        mock_stat_dataset.assert_any_call(dataset_name)
        mock_load_dataset.assert_any_call(dataset_name)

    @mock.patch(
        "datasets.datasets.stat_dataset",
        return_value={
            "columns": util.IRIS_COLUMNS,
            "featuretypes": util.IRIS_FEATURETYPES,
            "original-filename": util.IRIS_DATASET_NAME,
            "total": len(util.IRIS_DATA_ARRAY),
        },
    )
    @mock.patch(
        "datasets.datasets.load_dataset",
        return_value=util.IRIS_DATAFRAME,
    )
    def test_get_dataset_iris_csv_with_page_size_2_and_page_2(
        self, mock_load_dataset, mock_stat_dataset
    ):
        """
        Should return the 2nd page of size 2 from dataset contents.
        """
        dataset_name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.get(f"/datasets/{dataset_name}?page=2&page_size=2")
        result = rv.json()

        expected = {
            "columns": util.IRIS_COLUMNS_FEATURETYPES,
            "data": util.IRIS_DATA_ARRAY[2:4],
            "filename": util.IRIS_DATASET_NAME,
            "name": util.IRIS_DATASET_NAME,
            "total": len(util.IRIS_DATA_ARRAY),
        }
        self.assertEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
        mock_stat_dataset.assert_any_call(dataset_name)
        mock_load_dataset.assert_any_call(dataset_name)
