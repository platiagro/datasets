# -*- coding: utf-8 -*-
import io
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from datasets.api import app

import tests.util as util

TEST_CLIENT = TestClient(app)


class TestPatchDataset(unittest.TestCase):
    maxDiff = None

    @mock.patch(
        "datasets.datasets.stat_dataset",
        side_effect=util.FILE_NOT_FOUND_ERROR,
    )
    def test_patch_dataset_not_found(self, mock_stat_dataset):
        """
        Should raise http status 404 when given name does not exist.
        """
        dataset_name = "UNK"

        rv = TEST_CLIENT.patch(
            f"/datasets/{dataset_name}",
            files={
                "featuretypes": (
                    "featuretypes.txt",
                    io.StringIO(util.IRIS_FEATURETYPES_FILE),
                    "multipart/form-data",
                )
            },
        )
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
    @mock.patch(
        "datasets.datasets.update_dataset_metadata",
    )
    def test_patch_dataset_success(
        self, mock_update_dataset_metadata, mock_load_dataset, mock_stat_dataset
    ):
        """
        Should save metadata with given featuretypes file.
        """
        dataset_name = util.IRIS_DATASET_NAME

        rv = TEST_CLIENT.patch(
            f"/datasets/{dataset_name}",
            files={
                "featuretypes": (
                    "featuretypes.txt",
                    io.StringIO(util.IRIS_FEATURETYPES_FILE),
                    "multipart/form-data",
                )
            },
        )
        result = rv.json()

        expected = {
            "columns": util.IRIS_COLUMNS_FEATURETYPES,
            "data": util.IRIS_DATA_ARRAY,
            "filename": dataset_name,
            "name": dataset_name,
            "total": len(util.IRIS_DATA_ARRAY),
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_stat_dataset.assert_any_call(dataset_name)
        mock_load_dataset.assert_any_call(dataset_name)
        mock_update_dataset_metadata.assert_any_call(
            name=dataset_name,
            metadata={
                "columns": util.IRIS_COLUMNS,
                "featuretypes": util.IRIS_FEATURETYPES,
                "original-filename": util.IRIS_DATASET_NAME,
                "total": len(util.IRIS_DATA_ARRAY),
            },
        )
