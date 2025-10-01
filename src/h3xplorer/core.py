"""Main module."""

from pathlib import Path

import geopandas as gpd
import polars as pl


def _import_dataset(dataset_path: str | Path, separator: str = ",") -> pl.DataFrame:
    """Read an xy points file.

    Args:
        dataset_path: String or path of the dataset.
        separator: Separator for CSV file type.
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
    return read_func(dataset_path, **args)


def _read_xy_dataset(dataset: pl.DataFrame, x: str, y: str, epsg: int) -> pl.DataFrame:
    """Reads an xy dataset, converting it to lon/lat points if required.

    Args:
        dataset: DataFrame of data.
        x: The x / longitude field. Will try and guess this if not provided.
        y: The y / latitude field. Will try and guess this if not provided.
        epsg: The epsg to read the initial xy points from, if required.

    Raises:
        ValueError: If the 'x' and 'y' columns don't exist in the dataset
    """
    epsg_wgs84 = 4326
    lat = "lat"
    lon = "lon"

    missing_x = False
    missing_y = False
    if x not in dataset.columns:
        missing_x = True
    if y not in dataset.columns:
        missing_y = True
    if missing_x or missing_y:
        raise ValueError("'x' or 'y' columns are not included in the dataset")

    if epsg != epsg_wgs84:
        _epsg = f"EPSG:{epsg}"
        _x = dataset.select(x).to_series()
        _y = dataset.select(y).to_series()
        points_gdf = gpd.points_from_xy(_x, _y, crs=_epsg)
        points_gdf.to_crs(epsg=epsg_wgs84)
        points_gdf = points_gdf.to_crs(epsg=epsg_wgs84)
        _lon = points_gdf.x.tolist()
        _lat = points_gdf.y.tolist()
        dataset = dataset.with_columns([pl.Series(lon, _lon), pl.Series(lat, _lat)])
        dataset = dataset.drop(x, y)
    else:
        for input_name, col_name in {x: lon, y: lat}.items():
            if input_name is not col_name:
                dataset = dataset.drop(col_name, strict=False)
                dataset = dataset.rename({input_name: col_name})
    return dataset


def _get_hexagon_refs_for_points(
    df_input: pl.DataFrame, h3_size: int, h3_ref_field: str = "h3_ref"
) -> gpd.GeoDataFrame:
    """Gets the hexagons relevant to a set of point locations.

    This will both collect a set of hexagon references, and
    assign the spatial dataset given to those hexagon references
    as a new column named 'h3_ref' by default.

    Args:
        df_input: XY dataset to get hexagons of.
        h3_size: size of h3 hexagons to use.
        h3_ref_field: New field name for assigning h3 reference. If this already
            exists then it will rename the previous field with "_old" suffixed.
    """
    return gpd.GeoDataFrame()


def _get_hexagon_polygons(h3_refs: set) -> gpd.GeoDataFrame:
    """Turns a set of h3 references into a geodataframe of polygons.

    Args:
        h3_refs: set of h3 references.
    """
    return gpd.GeoDataFrame()


def _groupby_hexagons(
    input_gdf: gpd.GeoDataFrame, h3_ref_field: str = "h3_ref"
) -> gpd.GeoDataFrame:
    """Groups a dataset by the given reference field.

    Args:
        input_gdf: Spatial dataset for grouping.
        h3_ref_field: Column to group on.
    """
    return gpd.GeoDataFrame()


def _join_to_hexagon_polys():
    """Joins a set of polygons to the relevant dataset."""
    pass


def _plot_hexagons():
    pass
