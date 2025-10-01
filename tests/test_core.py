"""Tests for `h3xplorer` package."""

from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from h3xplorer import core


@pytest.fixture(scope="module")
def xy_dataset() -> pl.DataFrame:
    return pl.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "x": [300000, 400000, 500000, 530000, 400000],
        "y": [200000, 300000, 400000, 180000, 150000],
    })


@pytest.fixture(scope="module")
def latlon_dataset() -> pl.DataFrame:
    # verified co-ords using qgis to transform those in the xy_dataset
    return pl.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "lon": [-3.448079, -2.001428, -0.494362, -0.128329, -2.001375],
        "lat": [51.689821, 52.597808, 53.487243, 51.503992, 51.249166],
    })


class TestImportDataset:
    @pytest.fixture(scope="class")
    def test_files_path(self):
        return Path(__file__).parent / "fixture_data"

    def test_csv_returns_dataframe(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.csv")
        assert_frame_equal(df, xy_dataset)

    def test_csv_with_nondefault_separator_returns_dataframe(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy_semicolon.csv", separator=";")
        assert_frame_equal(df, xy_dataset)

    def test_parquet_returns_dataframe(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.parquet")
        assert_frame_equal(df, xy_dataset)

    def test_json_returns_dataframe(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.json")
        assert_frame_equal(df, xy_dataset)

    def test_ndjson_returns_dataframe(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.ndjson")
        assert_frame_equal(df, xy_dataset)

    def test_file_doesnt_exist_raises_error(self, test_files_path):
        with pytest.raises(FileNotFoundError, match="Dataset not found: *"):
            core._import_dataset(test_files_path / "xy.unknown")

    def test_unknown_extension_raises_error(self, test_files_path):
        with pytest.raises(ValueError, match="Dataset file type is not valid, given *"):
            core._import_dataset(test_files_path / "xy.other")


class TestReadXYDataset:
    def test_xy_dataset_missing_x_raises_error(self, xy_dataset):
        with pytest.raises(ValueError, match="'x' or 'y' columns are not included in the dataset"):
            core._read_xy_dataset(xy_dataset, "x_value", "y", 27700)

    def test_xy_dataset_missing_y_raises_error(self, xy_dataset):
        with pytest.raises(ValueError, match="'x' or 'y' columns are not included in the dataset"):
            core._read_xy_dataset(xy_dataset, "x", "y_value", 27700)

    def test_xy_dataset_missing_x_and_y_raises_error(self, xy_dataset):
        with pytest.raises(ValueError, match="'x' or 'y' columns are not included in the dataset"):
            core._read_xy_dataset(xy_dataset, "x_value", "y_value", 27700)

    def test_xy_dataset_returned_as_wgs84(self, xy_dataset, latlon_dataset):
        df = core._read_xy_dataset(xy_dataset, "x", "y", 27700)
        assert_frame_equal(df, latlon_dataset)

    def test_latlon_dataset_returned_unchanged(self, latlon_dataset):
        df = core._read_xy_dataset(latlon_dataset, "lon", "lat", 4326)
        assert_frame_equal(df, latlon_dataset)

    def test_latlon_dataset_with_alt_col_names_returned_unchanged(
        self, latlon_dataset: pl.DataFrame
    ):
        latlon_dataset = latlon_dataset.with_columns(
            pl.col("lon").alias("longitude"), pl.col("lat").alias("latitude")
        )
        df = core._read_xy_dataset(latlon_dataset, "longitude", "latitude", 4326)
        latlon_dataset = latlon_dataset.drop("longitude", "latitude")
        assert_frame_equal(df, latlon_dataset)


# if __name__ == "__main__":
#     xy_dataset().write_csv(Path(__file__).parent / "fixture_data" / "xy.csv")
#     xy_dataset().write_csv(Path(__file__).parent / "fixture_data" / "xy_semicolon.csv", separator=";")
#     xy_dataset().write_parquet(Path(__file__).parent / "fixture_data" / "xy.parquet")
#     xy_dataset().write_ndjson(Path(__file__).parent / "fixture_data" / "xy.ndjson")
#     xy_dataset().write_json(Path(__file__).parent / "fixture_data" / "xy.json")
