"""Explore point data as h3 hexagon aggregations."""

import logging
from pathlib import Path

import polars as pl
from lonboard import Map, basemap

from h3xplorer.data import (
    get_hexagon_polygons,
    get_hexagon_refs_for_points,
    groupby_ref_col,
    join_pldf_to_gdf,
)
from h3xplorer.inputs.points import xy_data_to_wgs84
from h3xplorer.inputs.table import read_dataset
from h3xplorer.mapping import create_polygon_layer

COL_LON = "lon"
COL_LAT = "lat"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def xy_plot(
    data_file: Path | pl.DataFrame,
    x_field: str,
    y_field: str,
    crs: int,
    hex_size: int,
    agg_field: str,
    agg_type: str,
    outfile: Path | None = None,
    **layer_properties,
) -> Map:
    """Plots an xy dataset as a lonboard map and optionally outputs to html.

    Args:
        data_file: path of the data file or polars dataframe containing the data.
            must contain 'x' and 'y' fields.
        x_field: the x (longitude) coordinates field.
        y_field: the y (latitude) coordinates field.
        crs: the coordinate reference system of the x and y coords.
            e.g. `4326` for WGS84, `27700` for British National Grid
        hex_size: The size of the `h3` hexagons to use.
            0 is very big, approx. country-size, 122 cells total worldwide.
            15 is very small, around 0.5m edges, 1m^2 area. approx. 570,000,000,000,000 worldwide.
            recommended:
            - 2 for country-regions (e.g. England),
            - 4 for local regions (English counties),
            - 6 for rural work (lsoa-ish),
            - 7-8 for urban work,
            - 10 for very local work (hectare).
        agg_field: Column to use for data (colours).
        agg_type: How to aggregate, will take any valid `polars` agg string e.g. `sum`, `mean`
        outfile: optional Path to an `.html` file location (can be new)
        layer_properties: additional keyword arguments to give to the layer being created.

    Returns:
        lonboard map with the layer displayed.
    """
    xys = read_dataset(data_file) if isinstance(data_file, Path) else data_file
    latlons = xy_data_to_wgs84(xys, x_field, y_field, crs)
    df_hex_refs, hex_refs = get_hexagon_refs_for_points(latlons, hex_size)
    hexes = get_hexagon_polygons(hex_refs)
    ref_field = f"{agg_field}_{agg_type}"
    aggregations = {ref_field: {"column": agg_field, "agg": agg_type}}
    df_agg = groupby_ref_col(df_hex_refs, ref_field="h3_ref", **aggregations)
    gdf = join_pldf_to_gdf(df_agg, hexes)
    layer = create_polygon_layer(gdf, ref_field, **layer_properties)
    m: Map = Map([layer], basemap_style=basemap.CartoBasemap.DarkMatter, show_tooltip=True)
    if outfile is not None:
        if not outfile.parent.exists():
            outfile.parent.mkdir()
        m.to_html(outfile, title=outfile.stem)
    return m
