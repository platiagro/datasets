# -*- coding: utf-8 -*-
from json import load

import pandas as pd
from platiagro import save_dataset
from platiagro.featuretypes import infer_featuretypes


def init_datasets(config_path):
    """Installs the datasets from a config file.

    Args:
        config_path (str): the path to the config file.
    """
    with open(config_path) as f:
        datasets = load(f)
        for dataset in datasets:
            name = dataset["name"]
            file = dataset["file"]
            filename = config_path.split("/")[-1]

            df = pd.read_csv(file)
            featuretypes = infer_featuretypes(df)
            metadata = {
                "featuretypes": featuretypes,
                "filename": filename,
            }
            # uses PlatIAgro SDK to save the dataset
            save_dataset(name, df, metadata=metadata)
