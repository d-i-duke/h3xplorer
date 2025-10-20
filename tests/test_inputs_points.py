"""Tests for `h3xplorer` inputs/points."""

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from h3xplorer.inputs.points import xy_data_to_wgs84


def make_xy_dataset() -> pl.DataFrame:
    return pl.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "x": [300000, 300000, 500000, 530000, 400000],
        "y": [200000, 200000, 400000, 180000, 150000],
    })


@pytest.fixture(scope="module")
def xy_dataset() -> pl.DataFrame:
    return make_xy_dataset()


@pytest.fixture(scope="module")
def latlon_dataset() -> pl.DataFrame:
    # verified co-ords using qgis to transform those in the xy_dataset (epsg 27700 -> 4326)
    return pl.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "lon": [-3.448079, -3.448079, -0.494362, -0.128329, -2.001375],
        "lat": [51.689821, 51.689821, 53.487243, 51.503992, 51.249166],
    })


class TestXYDataToWGS84:
    def test_xy_dataset_missing_x_raises_error(self, xy_dataset):
        with pytest.raises(ValueError, match="'x' or 'y' columns are not included in the dataset"):
            xy_data_to_wgs84(xy_dataset, "x_value", "y", 27700)

    def test_xy_dataset_missing_y_raises_error(self, xy_dataset):
        with pytest.raises(ValueError, match="'x' or 'y' columns are not included in the dataset"):
            xy_data_to_wgs84(xy_dataset, "x", "y_value", 27700)

    def test_xy_dataset_missing_x_and_y_raises_error(self, xy_dataset):
        with pytest.raises(ValueError, match="'x' or 'y' columns are not included in the dataset"):
            xy_data_to_wgs84(xy_dataset, "x_value", "y_value", 27700)

    def test_latlon_are_wrong_way_around_raises_error(self):
        input_df = pl.DataFrame({"lat": [-91], "lon": [1]})
        with pytest.raises(
            ValueError,
            match="Check lon and lat input col names, lon should be x and lat should be y",
        ):
            xy_data_to_wgs84(input_df, "lat", "lon", 4326)

    def test_lat_below_range_raises_error(self):
        input_df = pl.DataFrame({"lat": [-91], "lon": [1]})
        with pytest.raises(ValueError, match="lat and lon columns are outside plottable bounds *"):
            xy_data_to_wgs84(input_df, "lon", "lat", 4326)

    def test_lat_above_range_raises_error(self):
        input_df = pl.DataFrame({"lat": [91], "lon": [1]})
        with pytest.raises(ValueError, match="lat and lon columns are outside plottable bounds *"):
            xy_data_to_wgs84(input_df, "lon", "lat", 4326)

    def test_lon_below_range_raises_error(self):
        input_df = pl.DataFrame({"lat": [1], "lon": [-181]})
        with pytest.raises(ValueError, match="lat and lon columns are outside plottable bounds *"):
            xy_data_to_wgs84(input_df, "lon", "lat", 4326)

    def test_lon_above_range_raises_error(self):
        input_df = pl.DataFrame({"lat": [1], "lon": [-181]})
        with pytest.raises(ValueError, match="lat and lon columns are outside plottable bounds *"):
            xy_data_to_wgs84(input_df, "lon", "lat", 4326)

    def test_xy_dataset_returned_as_wgs84(self, xy_dataset, latlon_dataset):
        df = xy_data_to_wgs84(xy_dataset, "x", "y", 27700)
        assert_frame_equal(df, latlon_dataset)

    def test_latlon_dataset_returned_unchanged(self, latlon_dataset):
        df = xy_data_to_wgs84(latlon_dataset, "lon", "lat", 4326)
        assert_frame_equal(df, latlon_dataset)

    def test_latlon_dataset_with_alt_col_names_returned_unchanged(
        self, latlon_dataset: pl.DataFrame
    ):
        latlon_dataset = latlon_dataset.with_columns(
            pl.col("lon").alias("longitude"), pl.col("lat").alias("latitude")
        )
        df = xy_data_to_wgs84(latlon_dataset, "longitude", "latitude", 4326)
        latlon_dataset = latlon_dataset.drop("longitude", "latitude")
        assert_frame_equal(df, latlon_dataset)
