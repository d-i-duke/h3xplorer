"""Tests for `h3xplorer` inputs/table."""

from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from h3xplorer.inputs.table import read_dataset


def make_xy_dataset() -> pl.DataFrame:
    return pl.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "x": [300000, 300000, 500000, 530000, 400000],
        "y": [200000, 200000, 400000, 180000, 150000],
    })


@pytest.fixture(scope="module")
def xy_dataset() -> pl.DataFrame:
    return make_xy_dataset()


class TestImportDataset:
    @pytest.fixture(scope="class")
    def test_files_path(self):
        return Path(__file__).parent / "fixture_data"

    def test_csv_returns_dataframe(self, test_files_path, xy_dataset):
        df = read_dataset(test_files_path / "xy.csv")
        assert_frame_equal(df, xy_dataset)

    def test_csv_with_nondefault_separator_returns_dataframe(self, test_files_path, xy_dataset):
        df = read_dataset(test_files_path / "xy_semicolon.csv", separator=";")
        assert_frame_equal(df, xy_dataset)

    def test_parquet_returns_dataframe(self, test_files_path, xy_dataset):
        df = read_dataset(test_files_path / "xy.parquet")
        assert_frame_equal(df, xy_dataset)

    def test_json_returns_dataframe(self, test_files_path, xy_dataset):
        df = read_dataset(test_files_path / "xy.json")
        assert_frame_equal(df, xy_dataset)

    def test_ndjson_returns_dataframe(self, test_files_path, xy_dataset):
        df = read_dataset(test_files_path / "xy.ndjson")
        assert_frame_equal(df, xy_dataset)

    def test_file_doesnt_exist_raises_error(self, test_files_path):
        with pytest.raises(FileNotFoundError, match="Dataset not found: *"):
            read_dataset(test_files_path / "xy.unknown")

    def test_unknown_extension_raises_error(self, test_files_path):
        with pytest.raises(ValueError, match="Dataset file type is not valid, given *"):
            read_dataset(test_files_path / "xy.other")


if __name__ == "__main__":
    outdir = Path(__file__).parent / "fixture_data"
    data = make_xy_dataset()
    data.write_csv(outdir / "xy.csv")
    data.write_csv(outdir / "xy_semicolon.csv", separator=";")
    data.write_parquet(outdir / "xy.parquet")
    data.write_ndjson(outdir / "xy.ndjson")
    data.write_json(outdir / "xy.json")
