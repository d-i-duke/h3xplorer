"""Explore point data as h3 hexagon aggregations."""

import logging
from pathlib import Path

import geopandas as gpd
import h3.api.numpy_int as h3
import polars as pl
from tqdm import tqdm

COL_LON = "lon"
COL_LAT = "lat"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def _import_dataset(dataset_path: str | Path, separator: str = ",") -> pl.DataFrame:
    """Read an xy points file.

    Args:
        dataset_path: String or path of the dataset.
        separator: Separator for CSV file type.

    Returns:
        Imported dataset as a dataframe.
    """
    if isinstance(dataset_path, str):
        dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    suf = dataset_path.suffix
    args = {}

    if suf == ".parquet":
        read_func = pl.read_parquet
    elif suf in [".csv", ".csv.gz"]:
        read_func = pl.read_csv
        args["separator"] = separator
    elif suf == ".json":
        read_func = pl.read_json
    elif suf == ".ndjson":
        read_func = pl.read_ndjson
    else:
        raise ValueError(f"Dataset file type is not valid, given {suf})")
    logging.info(f"Loaded in dataset: {dataset_path.name}")
    return read_func(dataset_path, **args)


def _read_xy_dataset(dataset: pl.DataFrame, x: str, y: str, epsg: int) -> pl.DataFrame:
    """Reads an xy dataset, converting it to lon/lat points if required.

    Args:
        dataset: DataFrame of data.
        x: The x / longitude field. Will try and guess this if not provided.
        y: The y / latitude field. Will try and guess this if not provided.
        epsg: The epsg to read the initial xy points from, if required.

    Raises:
        ValueError: If the 'x' and 'y' columns don't exist in the dataset.
        ValueError: If the lat and lon results are outside standard bounds
            (-90 to +90, -180 to +180)

    Returns:
        Dataframe including "lat" and "lon" fields in EPSG:4326 (WGS84) format.
    """
    epsg_wgs84 = 4326

    missing_x = False
    missing_y = False
    if x not in dataset.columns:
        missing_x = True
    if y not in dataset.columns:
        missing_y = True
    if missing_x or missing_y:
        raise ValueError("'x' or 'y' columns are not included in the dataset")

    if x == COL_LAT or y == COL_LON:
        logging.warning("Check lon and lat input col names, lon should be x and lat should be y")

    if epsg != epsg_wgs84:
        logging.info("Converting points to EPSG:4326")
        _epsg = f"EPSG:{epsg}"
        _x = dataset.select(x).to_series()
        _y = dataset.select(y).to_series()
        points_gdf = gpd.points_from_xy(_x, _y, crs=_epsg)
        points_gdf.to_crs(epsg=epsg_wgs84)
        points_gdf = points_gdf.to_crs(epsg=epsg_wgs84)
        _lon = points_gdf.x.tolist()
        _lat = points_gdf.y.tolist()
        dataset = dataset.with_columns([pl.Series(COL_LON, _lon), pl.Series(COL_LAT, _lat)])
        dataset = dataset.drop(x, y)
        logging.info("Point conversion complete")
    else:
        for input_name, col_name in {x: COL_LON, y: COL_LAT}.items():
            # TODO: if lat and lon are the wrong way around this will error as it will drop the
            # lat column as part of the "x" fix
            if input_name is not col_name:
                dataset = dataset.drop(col_name, strict=False)
                dataset = dataset.rename({input_name: col_name})

    if (
        (dataset.select(COL_LAT).max().to_series().item() > 90)
        or (dataset.select(COL_LAT).min().to_series().item() < -90)
        or (dataset.select(COL_LON).max().to_series().item() > 180)
        or (dataset.select(COL_LON).min().to_series().item() < -180)
    ):
        raise ValueError(
            "lat and lon columns are outside plottable bounds (-90 to 90 for lat, -180 to 180 for lon)"
        )

    return dataset


def _get_hexagon_refs_for_points(
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
    refs = set()
    for idx in tqdm(range(len(lat)), "Converting points to h3 references"):
        refs.add(h3.latlng_to_cell(lat[idx], lon[idx], h3_size))
    df = df_input.clone()
    df = df.with_columns(pl.Series(h3_ref_field, list(refs)))
    logging.info("Hexagon references retrieved")
    return df, refs


def _get_hexagon_polygons(h3_refs: set | list) -> gpd.GeoDataFrame:
    """Turns a set of h3 references into a geodataframe of polygons.

    Args:
        h3_refs: set of h3 references.
    """
    refs = list(h3_refs) if isinstance(h3_refs, set) else h3_refs
    geoms = []
    for ref in tqdm(refs, "Converting h3 references to polygons"):
        geoms.append(h3.cells_to_h3shape([ref]))
    return gpd.GeoDataFrame({"h3_ref": refs, "geometry": geoms}, crs="EPSG:4326")


def _groupby_hexagons(
    input_df: pl.DataFrame, h3_ref_field: str = "h3_ref", **aggregations
) -> pl.DataFrame:
    """Groups a dataset by the given reference field and aggregations.

    Args:
        input_df: Dataset for grouping.
        h3_ref_field: Column to group on.
        **aggregations: kwargs dictionary of the form
            `"new_col"={"column": "column_name", "agg": "aggregation_type"}`
            when grouping.

    Returns:
        grouped dataframe of results, summarised by h3_ref_field.

    Raises:
        ValueError if the h3_ref_field is not present in the input_df.
        ValueError if any of the aggregation target columns are already in the input_df.
        ValueError if any of the aggregation columns are not present in the input_df.
    """
    col_str = "column"
    agg_str = "agg"

    if h3_ref_field not in input_df.columns:
        raise ValueError(
            f"h3_ref_field ({h3_ref_field}) must be in input_df column list ({input_df.columns})"
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

    logging.info("setting up aggregations:")
    aggs = {
        key: getattr(pl.col(values[col_str]), values[agg_str])()
        for key, values in aggregations.items()
    }
    logging.info(aggs)
    grouped = input_df.group_by(h3_ref_field).agg(**aggs)
    return grouped


def _join_to_hexagon_polys():
    """Joins a set of polygons to the relevant dataset."""
    pass


def _plot_hexagons():
    pass
