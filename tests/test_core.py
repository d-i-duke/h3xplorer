"""Tests for `h3xplorer` package."""

from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from h3xplorer import core


@pytest.fixture(scope="module")
def xy_dataset() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "x": [500000, 510000, 520000, 530000, 540000],
            "y": [200000, 210000, 190000, 180000, 220000],
        }
    )


@pytest.fixture(scope="module")
def latlon_dataset() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "lon": [0.0, 0.25, 0.5, -0.25, -0.5],
            "lat": [52.0, 51.5, 52.5, 53.0, 53.5],
        }
    )


class TestImportDataset:
    @pytest.fixture(scope="class")
    def test_files_path(self):
        return Path(__file__).parent / "fixture_data"

    def test_csv_reads_correctly(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.csv")
        assert_frame_equal(df, xy_dataset)

    def test_csv_with_nondefault_separator_reads_correctly(self, test_files_path, xy_dataset):
        df = core._import_dataset(
            test_files_path / "xy_semicolon.csv",
            separator=";",
        )
        assert_frame_equal(df, xy_dataset)

    def test_parquet_reads_correctly(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.parquet")
        assert_frame_equal(df, xy_dataset)

    def test_json_reads_correctly(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.json")
        assert_frame_equal(df, xy_dataset)

    def test_ndjson_reads_correctly(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.ndjson")
        assert_frame_equal(df, xy_dataset)


# if __name__ == "__main__":
#     xy_dataset().write_csv(Path(__file__).parent / "fixture_data" / "xy.csv")
#     xy_dataset().write_csv(Path(__file__).parent / "fixture_data" / "xy_semicolon.csv", separator=";")
#     xy_dataset().write_parquet(Path(__file__).parent / "fixture_data" / "xy.parquet")
#     xy_dataset().write_ndjson(Path(__file__).parent / "fixture_data" / "xy.ndjson")
#     xy_dataset().write_json(Path(__file__).parent / "fixture_data" / "xy.json")
