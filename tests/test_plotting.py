"""Tests for `h3xplorer` plotting."""

import pytest

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
        rgb = plotting.to_rgb("ff2a00")
        expected = [255, 42, 0]
        assert rgb == expected

    def test_hex_string_converts_as_expected(self):
        rgb = plotting.to_rgb("#ff2a00")
        expected = [255, 42, 0]
        assert rgb == expected


class TestToPalette:
    pass


class TestNormaliseValues:
    pass


class TestPlotPolygonData:
    pass
