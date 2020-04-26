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

            df = pd.read_csv(file, sep=None, engine="python")
            columns = df.columns.values.tolist()
            featuretypes = infer_featuretypes(df)
            metadata = {
                "columns": columns,
                "featuretypes": featuretypes,
                "original-filename": filename,
            }
            try:
                # uses PlatIAgro SDK to save the dataset
                # marks as read only, so users can't mess with these datasets
                save_dataset(name, df, metadata=metadata, read_only=True)
            except PermissionError:
                pass
