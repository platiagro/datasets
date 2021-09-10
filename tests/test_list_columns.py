# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from datasets.api import app

import tests.util as util

TEST_CLIENT = TestClient(app)


class TestListColumns(unittest.TestCase):
    @mock.patch(
        "datasets.columns.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    def test_list_columns_file_not_found(self, mock_stat_dataset):
        """
        Should raise http status 404 when given name does not exist.
        """
        dataset_name = "UNK"
        rv = TEST_CLIENT.get(f"/datasets/{dataset_name}/columns")

        result = rv.json()
        expected = {"message": "The specified dataset does not exist"}

        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)
        mock_stat_dataset.assert_any_call(dataset_name)

    @mock.patch(
        "datasets.columns.stat_dataset",
        return_value={
            "columns": util.IRIS_COLUMNS,
            "featuretypes": util.IRIS_FEATURETYPES,
            "original-filename": util.IRIS_DATASET_NAME,
            "total": len(util.IRIS_DATA_ARRAY),
        },
    )
    def test_list_columns_success(self, mock_stat_dataset):
        """
        Should return a list of columns for a given dataset.
        """
        dataset_name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.get(f"/datasets/{dataset_name}/columns")
        result = rv.json()

        expected = util.IRIS_COLUMNS_FEATURETYPES
        self.assertListEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
        mock_stat_dataset.assert_any_call(dataset_name)
