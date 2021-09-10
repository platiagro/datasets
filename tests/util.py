# -*- coding: utf-8 -*-
import pandas as pd

IRIS_DATASET_NAME = "iris.csv"

IRIS_DATA = (
    "SepalLengthCm,SepalWidthCm,PetalLengthCm,PetalWidthCm,Species\n"
    "5.1,3.5,1.4,0.2,Iris-setosa\n"
    "4.9,3.0,1.4,0.2,Iris-setosa\n"
    "4.7,3.2,1.3,0.2,Iris-setosa\n"
    "4.6,3.1,1.5,0.2,Iris-setosa\n"
)

IRIS_DATA_ARRAY = [
    [5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
    [4.9, 3.0, 1.4, 0.2, "Iris-setosa"],
    [4.7, 3.2, 1.3, 0.2, "Iris-setosa"],
    [4.6, 3.1, 1.5, 0.2, "Iris-setosa"],
]

IRIS_COLUMNS = [
    "SepalLengthCm",
    "SepalWidthCm",
    "PetalLengthCm",
    "PetalWidthCm",
    "Species",
]

IRIS_FEATURETYPES = [
    "Numerical",
    "Numerical",
    "Numerical",
    "Numerical",
    "Categorical",
]

IRIS_FEATURETYPES_FILE = "Numerical\nNumerical\nNumerical\nNumerical\nCategorical\n"

IRIS_COLUMNS_FEATURETYPES = [
    {"featuretype": "Numerical", "name": "SepalLengthCm"},
    {"featuretype": "Numerical", "name": "SepalWidthCm"},
    {"featuretype": "Numerical", "name": "PetalLengthCm"},
    {"featuretype": "Numerical", "name": "PetalWidthCm"},
    {"featuretype": "Categorical", "name": "Species"},
]

IRIS_DATAFRAME = pd.DataFrame(IRIS_DATA_ARRAY, columns=IRIS_COLUMNS)

PNG_DATASET_NAME = "text.png"

PNG_DATA = open(f"tests/resources/{PNG_DATASET_NAME}", "rb").read()

FILE_NOT_FOUND_ERROR = FileNotFoundError("The specified dataset does not exist")