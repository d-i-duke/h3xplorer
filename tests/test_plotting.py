"""Tests for `h3xplorer` plotting."""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from lonboard import PolygonLayer
from numpy.testing import assert_array_equal
from shapely import Polygon

from h3xplorer import plotting


@pytest.fixture(scope="module")
def data_list():
    return [-5, 0, 5, 10]


@pytest.fixture(scope="module")
def data_series(data_list):
    return pd.Series(data_list)


class TestToRGB:
    def test_hex_string_too_short_without_hash_raises_error(self):
        with pytest.raises(ValueError, match="Hex string must be 6 active characters*"):
            plotting.to_rgb("fffff")

    def test_hex_string_too_short_with_hash_raises_error(self):
        with pytest.raises(ValueError, match="Hex string must be 6 active characters*"):
            plotting.to_rgb("#fffff")

    def test_hex_string_too_long_without_hash_raises_error(self):
        with pytest.raises(ValueError, match="Hex string must be 6 active characters*"):
            plotting.to_rgb("fffffff")

    def test_hex_string_too_long_with_hash_raises_error(self):
        with pytest.raises(ValueError, match="Hex string must be 6 active characters*"):
            plotting.to_rgb("ffffffff")

    def test_hex_string_with_non_hex_chars_raises_error(self):
        with pytest.raises(ValueError, match="Hex string must only include 0-9 and a-f characters"):
            plotting.to_rgb("#ffgfff")

    def test_hex_string_without_hash_converts_as_expected(self):
        rgb = plotting.to_rgb("ffaa00")
        expected = [255, 170, 0]
        assert rgb == expected

    def test_hex_string_converts_as_expected(self):
        rgb = plotting.to_rgb("#ffaa00")
        expected = [255, 170, 0]
        assert rgb == expected


class TestToPalette:
    @pytest.fixture(scope="class")
    def cmap_hex(self):
        return ["#000000", "#FFFFFF"]

    @pytest.fixture(scope="class")
    def name(self):
        return "colorcet"

    def test_typical_cmap_creates_expected_name(self, cmap_hex, name):
        result = plotting.colorcet_to_palette(cmap_hex)
        assert result.name == name

    def test_typical_cmap_creates_expected_maptype(self, cmap_hex, name):
        result = plotting.colorcet_to_palette(cmap_hex)
        assert result.type == name

    def test_typical_cmap_creates_expected_hex_colors(self, cmap_hex):
        result = plotting.colorcet_to_palette(cmap_hex)
        assert result.hex_colors == cmap_hex

    def test_typical_cmap_creates_expected_mpl_colors(self, cmap_hex):
        cmap_rgb = [(0, 0, 0), (1, 1, 1)]
        result = plotting.colorcet_to_palette(cmap_hex)
        assert result.mpl_colors == cmap_rgb


class TestNormaliseValues:
    def test_no_max_threshold_returns_expected(self, data_series):
        assert_array_equal(
            plotting.normalise_values_diverging(data_series), np.array([0.25, 0.5, 0.75, 1])
        )

    def test_int_max_threshold_returns_expected(self, data_series):
        assert_array_equal(
            plotting.normalise_values_diverging(data_series, 5), np.array([0, 0.5, 1, 1.5])
        )

    def test_negative_float_max_threshold_returns_expected(self, data_series):
        # values converted so that 0 = -0.25, 1 = +0.25.
        # this makes 10 = 0.5 + (0.5*4) = 2.5
        assert_array_equal(
            plotting.normalise_values_diverging(data_series, -2.5), np.array([-0.5, 0.5, 1.5, 2.5])
        )


class TestCreatePolygonLayer:
    @pytest.fixture(scope="class")
    def poly_coords(self):
        # this is the equivalent of
        # gpd.points_from_xy([-0.5, 0, 0.5, 1], [51, 51.2, 50.8, 50.9]).buffer(0.1, 1)
        return [
            [(-0.4, 51.0), (-0.5, 50.9), (-0.6, 51.0), (-0.5, 51.1), (-0.4, 51.0)],
            [(0.1, 51.2), (0.0, 51.1), (-0.1, 51.2), (0.0, 51.3), (0.1, 51.2)],
            [(0.6, 50.8), (0.5, 50.7), (0.4, 50.8), (0.5, 50.9), (0.6, 50.8)],
            [(1.1, 50.9), (1.0, 50.8), (0.9, 50.9), (1.0, 51.0), (1.1, 50.9)],
        ]

    @pytest.fixture(scope="class")
    def gdf(self, data_series, poly_coords):
        return gpd.GeoDataFrame(
            {"data": data_series},
            geometry=[Polygon(coords) for coords in poly_coords],
            crs="EPSG:4326",
        )

    @pytest.fixture(scope="class")
    def default_layer(self, gdf):
        return plotting.create_polygon_layer(gdf, "data")

    @pytest.fixture(scope="class")
    def default_fill_colors(self):
        return [
            [168, 190, 248, 191],
            [237, 236, 236, 191],
            [209, 189, 131, 191],
            [167, 143, 8, 191],
        ]

    @pytest.fixture(scope="class")
    def default_line_colors(self):
        return [
            [168, 190, 248, 229],
            [237, 236, 236, 229],
            [209, 189, 131, 229],
            [167, 143, 8, 229],
        ]

    def test_default_settings_creates_expected_data_type(self, default_layer):
        assert isinstance(default_layer, PolygonLayer)

    def test_default_settings_create_expected_table_structure(self, default_layer):
        table = default_layer.table
        assert table.column_names == ["data", "geometry"]
        assert table.shape == (4, 2)

    def test_default_settings_creates_expected_data_in_table(self, default_layer, data_list):
        table = default_layer.table
        assert [table[0][num].as_py() for num in range(4)] == data_list

    def test_default_settings_creates_expected_geoms_in_table(self, default_layer, poly_coords):
        table = default_layer.table
        assert [table[1][num].as_py() for num in range(4)] == [
            [[[coord for coord in coord_tuple] for coord_tuple in coord_list]]
            for coord_list in poly_coords
        ]

    def test_default_settings_creates_expected_formatting(
        self, default_layer, default_fill_colors, default_line_colors
    ):
        assert default_layer.get_line_width == 5
        assert default_layer.line_width_min_pixels == 2
        assert default_layer.line_width_max_pixels == 5
        assert [
            default_layer.get_fill_color[num].as_py() for num in range(4)
        ] == default_fill_colors
        assert [
            default_layer.get_line_color[num].as_py() for num in range(4)
        ] == default_line_colors

    def test_custom_overwrite_formatting_creates_overwritten_format(
        self, gdf, default_fill_colors, default_line_colors
    ):
        test_num = 100
        layer = plotting.create_polygon_layer(gdf, "data", get_line_width=test_num)
        assert layer.get_line_width == test_num
        assert layer.line_width_min_pixels == 2
        assert layer.line_width_max_pixels == 5
        assert [layer.get_fill_color[num].as_py() for num in range(4)] == default_fill_colors
        assert [layer.get_line_color[num].as_py() for num in range(4)] == default_line_colors

    def test_custom_new_formatting_creates_addiitonal_formatting(
        self, gdf, default_fill_colors, default_line_colors
    ):
        test_settings = {"get_elevation": np.array([1, 1, 10, 20]), "extruded": True}
        layer = plotting.create_polygon_layer(gdf, "data", **test_settings)
        assert layer.get_line_width == 5
        assert layer.line_width_min_pixels == 2
        assert layer.line_width_max_pixels == 5
        assert [layer.get_fill_color[num].as_py() for num in range(4)] == default_fill_colors
        assert [layer.get_line_color[num].as_py() for num in range(4)] == default_line_colors
        assert_array_equal(layer.get_elevation, test_settings["get_elevation"])
        assert layer.extruded == test_settings["extruded"]

    def test_max_threshold_creates_expected_fill_colors(self, gdf):
        layer = plotting.create_polygon_layer(gdf, "data", max_threshold=20)
        assert [layer.get_fill_color[num].as_py() for num in range(4)] == [
            [206, 215, 244, 191],
            [237, 236, 236, 191],
            [226, 214, 184, 191],
            [209, 189, 131, 191],
        ]

    def test_custom_cmap_creates_expected_colors(self, gdf):
        layer = plotting.create_polygon_layer(gdf, "data", cmap=["#ffffff", "#ffffff"])
        assert [layer.get_fill_color[num].as_py() for num in range(4)] == [
            [255, 255, 255, 191] for _ in range(4)
        ]
        assert [layer.get_line_color[num].as_py() for num in range(4)] == [
            [255, 255, 255, 229] for _ in range(4)
        ]
