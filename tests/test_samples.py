# -*- coding: utf-8 -*-
import os
from json import dump
from unittest import TestCase

from datasets.samples import init_datasets


class TestSamples(TestCase):

    def setUp(self):
        with open("config.json", "w+") as f:
            data = [
                {
                    "name": "sample",
                    "file": "sample.csv",
                }
            ]
            dump(data, f)

        with open("sample.csv", "w+") as f:
            f.write("2010,0.1,class1\n" +
                    "2011,0.2,class2\n")

    def tearDown(self):
        os.remove("sample.csv")
        os.remove("config.json")

    def test_init_datasets(self):
        init_datasets("config.json")
