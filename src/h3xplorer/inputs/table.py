"""Imports data tables."""

import logging
from pathlib import Path

import polars as pl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def read_dataset(dataset_path: str | Path, separator: str = ",") -> pl.DataFrame:
    """Read a data table file.

    Args:
        dataset_path: String or path of the dataset.
        separator: Separator for CSV file type.

    Returns:
        Imported dataset as a dataframe.
    """
    if isinstance(dataset_path, str):
        dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    suf = dataset_path.suffix
    args = {}

    if suf == ".parquet":
        read_func = pl.read_parquet
    elif suf in [".csv", ".csv.gz"]:
        read_func = pl.read_csv
        args["separator"] = separator
    elif suf == ".json":
        read_func = pl.read_json
    elif suf == ".ndjson":
        read_func = pl.read_ndjson
    else:
        raise ValueError(f"Dataset file type is not valid, given {suf})")
    logging.info(f"Loaded in dataset: {dataset_path.name}")
    return read_func(dataset_path, **args)
