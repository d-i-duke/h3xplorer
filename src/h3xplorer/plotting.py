"""Contains functions for plotting data."""

import re

import colorcet as cc
import geopandas as gpd
import numpy as np
import pandas as pd
from lonboard import PolygonLayer
from lonboard.colormap import apply_continuous_cmap
from numpy._typing import NDArray
from palettable.palette import Palette


def to_rgb(hex: str) -> list[int]:
    """Converts a hex string to an RGB list.

    Args:
        hex: string representation of a hex number.

    Raises:
        ValueError if the string is not 6 characters long (after stripping '#' characters).
        ValueError if the string contains any non 0-9, a-f characters.

    Returns:
        list of Red, Green, Blue numbers each between 0 and 255.
    """
    h = hex.strip("#")
    if len(h) != 6:
        raise ValueError("Hex string must be 6 active characters in length (ignoring '#')")
    if not bool(re.fullmatch(r"[0-9a-fA-F]+", h)):
        raise ValueError("Hex string must only include 0-9 and a-f characters")
    return list(int(h[i : i + 2], 16) for i in (0, 2, 4))


def colorcet_to_palette(cmap: list[str]) -> Palette:
    """Returns the ColorCet colormap as a palettable Palette.

    Args:
        cmap: list of hex-format color values in order. can be generated with colorcet or similar.

    Returns:
        Palettable Palette object using the given colour map information.
    """
    colors = [to_rgb(item) for item in cmap]
    return Palette(name="colorcet", map_type="colorcet", colors=colors)


def normalise_values_diverging(
    data_values: pd.Series, max_threshold: float | int | None = None
) -> NDArray:
    """Normalises a set of values into a 0-1 range.

    This will convert anything > 0 into the 0.5-1.0 range, and <0 into the 0-0.5 range,
    which allows usage of diverging colourschemes.

    Args:
        data_values: A series of numerical values.
        max_threshold: A value to set max/min at in the new normalised set of values. This can
            make values in the return NDArray be below 0 / above 1.
            If a max threshold is negative it will be made positive using `abs()`.

    Returns:
        A numpy NDArray of values between 0 and 1.
    """
    if max_threshold is None:
        norm_values = data_values / max(abs(data_values.max()), abs(data_values.min()))
    else:
        norm_values = data_values / abs(max_threshold)
    norm_values = np.array([(value + 1) / 2 for value in norm_values])
    return norm_values


def create_polygon_layer(
    gdf: gpd.GeoDataFrame,
    value_col: str,
    max_threshold: float | int | None = None,
    cmap: list[str] | None = None,
    **polygon_formatting,
) -> PolygonLayer:
    """Creates a polygon layer for the given data.

    Colours are plotted using a diverging colour scheme, where by default colours below zero
    are plotted in blue, and colours above zero are plotted in brown. The default colour scheme
    was chosen for accessibility.

    Args:
        gdf: Spatial dataset containing only polygons.
        value_col: value of the column to use for colours.
        max_threshold: A value to set max/min at in the new normalised set of values. This can
            make values in the return NDArray be below 0 / above 1.
            If a max threshold is negative it will be made positive using `abs()`.
        cmap: the colour map to use. by default this will use the colorcet cmap 'CET_CBL1'.
        **polygon_formatting: Dictionary of PolygonLayer formatting options to their values.

    Returns:
        lonboard-format polygon layer with the given formatting applied.
    """
    cmap = cc.CET_CBL1 if cmap is None else cmap
    palette = colorcet_to_palette(cmap)
    data_values = gdf.loc[:, value_col]
    norm_values = normalise_values_diverging(data_values, max_threshold)
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
    return PolygonLayer.from_geopandas(gdf, **polygon_formatting_to_apply)
