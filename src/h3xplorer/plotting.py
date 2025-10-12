"""Contains functions for plotting data."""

import re

import colorcet as cc
import geopandas as gpd
import numpy as np
from lonboard import Map, PolygonLayer, basemap
from lonboard.colormap import apply_continuous_cmap
from numpy._typing import NDArray
from palettable.palette import Palette


def to_rgb(hex: str) -> list:
    """Converts a hex string to an RGB list."""
    h = hex.strip("#")
    if len(h) != 6:
        raise ValueError("Hex string must be 6 active characters in length (ignoring '#')")
    if not bool(re.fullmatch(r"[0-9a-fA-F]+", h)):
        raise ValueError("Hex string must only include 0-9 and a-f characters")
    return list(int(h[i : i + 2], 16) for i in (0, 2, 4))


def to_palette(cmap) -> Palette:
    """Returns the ColorCet colormap as a palettable Palette."""
    colors = [to_rgb(item) for item in cmap]
    return Palette(name="colorcet", map_type="colorcet", colors=colors)


def normalise_values(df, col) -> NDArray:
    """Normalises a set of values into a 0-1 range."""
    data_values = df.loc[:, col]
    norm_values = data_values / max(abs(data_values.max()), abs(data_values.min()))
    norm_values = np.array([(value + 1) / 2 for value in norm_values])
    return norm_values


def plot_polygon_data(gdf: gpd.GeoDataFrame, value_col: str, **polygon_formatting) -> Map:
    """Creates a lonboard map plotting the given polygon data.

    Args:
        gdf: Spatial dataset containing only polygons.
        value_col: value of the column in the
        **polygon_formatting: Dictionary of PolygonLayer formatting options to their values.

    Returns:
        lonboard map with the given polygon data plotted.
    """
    palette = to_palette(cc.CET_CBD1)
    norm_values = normalise_values(gdf, value_col)
    fill_colours = apply_continuous_cmap(norm_values, palette, alpha=0.75)
    line_colours = apply_continuous_cmap(norm_values, palette, alpha=0.9)
    default_format = {
        "get_line_width": 5,
        "line_width_min_pixels": 2,
        "line_width_max_pixels": 5,
        "get_fill_color": fill_colours,
        "get_line_color": line_colours,
    }
    polygon_formatting_to_apply = default_format | polygon_formatting

    layer = PolygonLayer.from_geopandas(gdf, **polygon_formatting_to_apply)
    m = Map([layer], basemap_style=basemap.CartoBasemap.DarkMatter)
    return m
