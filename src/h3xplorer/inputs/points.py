"""Imports point-based datasets."""

import logging

import geopandas as gpd
import polars as pl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

COL_LON = "lon"
COL_LAT = "lat"


def xy_data_to_wgs84(dataset: pl.DataFrame, x: str, y: str, epsg: int) -> pl.DataFrame:
    """Reads an xy dataset, converting it to lon/lat points if required.

    Args:
        dataset: DataFrame of data.
        x: The x / longitude field. Will try and guess this if not provided.
        y: The y / latitude field. Will try and guess this if not provided.
        epsg: The epsg to read the initial xy points from, if required.

    Raises:
        ValueError: If the 'x' and 'y' columns don't exist in the dataset.
        ValueError: If the 'lat' and 'lon' columns are the wrong way around:
            ('lon' should be x, 'lat' should be y)
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
        raise ValueError("Check lon and lat input col names, lon should be x and lat should be y")

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
