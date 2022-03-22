# -*- coding: utf-8 -*-
from datasets.api import app
from fastapi.testclient import TestClient
import unittest
import os

os.environ["ENABLE_CORS"] = "1"


TEST_CLIENT = TestClient(app)


class TestCors(unittest.TestCase):
    def test_ping_with_cors_enabled(self):
        """
        Should CORS headers, http status 200 OK, and text "pong".
        """
        rv = TEST_CLIENT.get("/")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.text, "pong")

        self.assertTrue("Access-Control-Allow-Origin" in rv.headers)
        self.assertTrue("Access-Control-Allow-Methods" in rv.headers)
        self.assertTrue("Access-Control-Allow-Headers" in rv.headers)
