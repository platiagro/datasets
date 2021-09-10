# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from datasets.api import app

import tests.util as util

TEST_CLIENT = TestClient(app)


class TestListDatasets(unittest.TestCase):
    @mock.patch(
        "platiagro.list_datasets",
        return_value=[util.IRIS_DATASET_NAME],
    )
    def test_list_datasets_success(self, mock_list_datasets):
        """
        Should list a single dataset named "iris.csv".
        """
        rv = TEST_CLIENT.get("/datasets")
        result = rv.json()

        expected = [{"name": util.IRIS_DATASET_NAME}]
        self.assertEqual(result, expected)

        mock_list_datasets.assert_any_call()
