import unittest

from datasets.api import ping


class TestApi(unittest.TestCase):

    def test_ping(self):
        result = ping()
        expected = "pong"
        self.assertEqual(result, expected)
