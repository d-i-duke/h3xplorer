"""Tests for `h3xplorer` plotting."""

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_array_equal

from h3xplorer import plotting


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
    @pytest.fixture(scope="class")
    def series(self):
        return pd.Series([-5, 0, 5, 10])

    def test_no_max_threshold_returns_expected(self, series):
        assert_array_equal(
            plotting.normalise_values_diverging(series), np.array([0.25, 0.5, 0.75, 1])
        )

    def test_int_max_threshold_returns_expected(self, series):
        assert_array_equal(
            plotting.normalise_values_diverging(series, 5), np.array([0, 0.5, 1, 1.5])
        )

    def test_negative_float_max_threshold_returns_expected(self, series):
        # values converted so that 0 = -0.25, 1 = +0.25.
        # this makes 10 = 0.5 + (0.5*4) = 2.5
        assert_array_equal(
            plotting.normalise_values_diverging(series, -2.5), np.array([-0.5, 0.5, 1.5, 2.5])
        )


class TestCreatePolygonLayer:
    pass
