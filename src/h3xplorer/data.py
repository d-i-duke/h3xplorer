"""Manage datasets."""

import logging

import geopandas as gpd
import h3.api.numpy_int as h3
import polars as pl
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

COL_LON = "lon"
COL_LAT = "lat"


def get_hexagon_refs_for_points(
    df_input: pl.DataFrame, h3_size: int, h3_ref_field: str = "h3_ref"
) -> tuple[pl.DataFrame, set]:
    """Gets the hexagons relevant to a set of point locations.

    This will both collect a set of hexagon references, and
    assign the spatial dataset given to those hexagon references
    as a new column named 'h3_ref' by default.

    Args:
        df_input: XY dataset to get hexagons of.
        h3_size: size of h3 hexagons to use.
        h3_ref_field: New field name for assigning h3 reference. If this already
            exists then it will rename the previous field with "_old" suffixed.

    Returns:
        Clone of the dataframe with a new h3 reference field for each record, and
        set of h3 references.
    """
    logging.info("Getting hexagon references")
    lat = df_input.select(COL_LAT).to_series()
    lon = df_input.select(COL_LON).to_series()
    refs = []
    for idx in tqdm(range(len(lat)), "Converting points to h3 references"):
        refs.append(h3.latlng_to_cell(lat[idx], lon[idx], h3_size))
    df = df_input.clone()
    df = df.with_columns(pl.Series(h3_ref_field, refs))
    logging.info("Hexagon references retrieved")
    return df, set(refs)


def get_hexagon_polygons(h3_refs: set | list) -> gpd.GeoDataFrame:
    """Turns a set of h3 references into a geodataframe of polygons.

    Args:
        h3_refs: set of h3 references.
    """
    logging.info("Creating hexagon polygons table")
    refs = list(h3_refs) if isinstance(h3_refs, set) else h3_refs
    geoms = []
    for ref in tqdm(refs, "Converting h3 references to polygons"):
        geoms.append(h3.cells_to_h3shape([ref]))
    return gpd.GeoDataFrame({"h3_ref": refs, "geometry": geoms}, crs="EPSG:4326")


def groupby_ref_col(
    input_df: pl.DataFrame, ref_field: str = "h3_ref", **aggregations
) -> pl.DataFrame:
    """Groups a dataset by the given reference field and aggregations.

    Args:
        input_df: Dataset for grouping.
        ref_field: Column to group on.
        **aggregations: kwargs dictionary of the form
            `"new_col"={"column": "column_name", "agg": "aggregation_type"}`
            when grouping.

    Returns:
        grouped dataframe of results, summarised by ref_field.

    Raises:
        ValueError if the ref_field is not present in the input_df.
        ValueError if any of the aggregation target columns are already in the input_df.
        ValueError if any of the aggregation columns are not present in the input_df.
    """
    col_str = "column"
    agg_str = "agg"

    if ref_field not in input_df.columns:
        raise ValueError(
            f"ref_field ({ref_field}) must be in input_df column list ({input_df.columns})"
        )

    duplicate_cols = []
    for new_col in aggregations:
        if new_col in input_df.columns:
            logging.debug(f"duplicate: {new_col}, {input_df.columns}")
            duplicate_cols.append(new_col)
    if len(duplicate_cols) > 0:
        raise ValueError(
            f"some of the target aggregations column names are duplicates from input_df ({duplicate_cols})"
        )

    missing_cols = []
    for values in aggregations.values():
        if (col := values[col_str]) not in input_df.columns:
            logging.debug(f"missing: {col}, {input_df.columns}")
            missing_cols.append(col)
    if len(missing_cols) > 0:
        raise ValueError(
            f"some of the aggregations column names are missing from the input_df ({missing_cols})"
        )

    aggs = {
        key: getattr(pl.col(values[col_str]), values[agg_str])()
        for key, values in aggregations.items()
    }
    logging.debug(aggs)
    logging.info("aggregating data input to spatial areas")
    grouped = input_df.group_by(ref_field).agg(**aggs)
    return grouped


def join_pldf_to_gdf(
    df: pl.DataFrame, gdf: gpd.GeoDataFrame, ref_col: str = "h3_ref"
) -> gpd.GeoDataFrame:
    """Joins a polars dataframe to a geodataframe.

    Args:
        df: table of data.
        gdf: spatial data.
        ref_col: column present in both df and gdf to join on.

    Returns:
        GeoDataFrame with table of data attached.

    Raises:
        ValueError if ref_col not in df or gdf
    """
    if ref_col not in df.columns or ref_col not in gdf.columns:
        raise ValueError("ref_col missing in df and/or gdf")
    df_to_join = df.to_pandas().set_index(ref_col)
    gdf_to_join = gdf.set_index(ref_col)
    logging.debug(df_to_join)
    logging.debug(gdf_to_join)
    gdf_joined = gdf_to_join.join(df_to_join)
    logging.debug(gdf_joined)
    return gdf_joined
