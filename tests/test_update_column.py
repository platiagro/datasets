# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from datasets.api import app

import tests.util as util

TEST_CLIENT = TestClient(app)


class TestUpdateColumn(unittest.TestCase):
    @mock.patch(
        "datasets.columns.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    def test_update_column_dataset_not_found(self, mock_stat_dataset):
        """
        Should raise http status 404 when given dataset name does not exist.
        """
        dataset_name = util.IRIS_DATASET_NAME
        column_name = "col0"

        rv = TEST_CLIENT.patch(
            f"/datasets/{dataset_name}/columns/{column_name}",
            json={"featuretype": "Numerical"},
        )
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
    def test_update_column_column_not_found(self, mock_stat_dataset):
        """
        Should raise http status 404 when given column does not exist.
        """
        dataset_name = util.IRIS_DATASET_NAME
        column_name = "col0"

        rv = TEST_CLIENT.patch(
            f"/datasets/{dataset_name}/columns/{column_name}",
            json={"featuretype": "Numerical"},
        )
        result = rv.json()
        expected = {"message": "The specified column does not exist"}

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
    def test_update_column_invalid_featuretype(self, mock_stat_dataset):
        """
        Should raise http status 400 when given featuretype is invalid.
        """
        dataset_name = util.IRIS_DATASET_NAME
        column_name = "Species"

        rv = TEST_CLIENT.patch(
            f"/datasets/{dataset_name}/columns/{column_name}",
            json={"featuretype": "Invalid"},
        )
        result = rv.json()

        expected = {
            "message": "featuretype must be one of DateTime, Numerical, Categorical"
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)
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
    @mock.patch(
        "datasets.columns.load_dataset",
        return_value=util.IRIS_DATAFRAME,
    )
    @mock.patch(
        "datasets.columns.save_dataset",
        return_value=util.IRIS_DATAFRAME,
    )
    def test_update_column_success(
        self, mock_save_dataset, mock_load_dataset, mock_stat_dataset
    ):
        """
        Should update metadata successfully.
        """
        dataset_name = util.IRIS_DATASET_NAME
        column_name = "Species"

        rv = TEST_CLIENT.patch(
            f"/datasets/{dataset_name}/columns/{column_name}",
            json={"featuretype": "Numerical"},
        )
        result = rv.json()

        expected = {"name": column_name, "featuretype": "Numerical"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_stat_dataset.assert_any_call(dataset_name)

        mock_load_dataset.assert_any_call(dataset_name)

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
