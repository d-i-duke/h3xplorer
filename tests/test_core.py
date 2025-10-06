"""Tests for `h3xplorer` package."""

from pathlib import Path

import geopandas as gpd
import polars as pl
import pytest
from geopandas.testing import assert_geodataframe_equal
from polars.testing import assert_frame_equal, assert_series_equal
from shapely import Polygon

from h3xplorer import core


@pytest.fixture(scope="module")
def xy_dataset() -> pl.DataFrame:
    return pl.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "x": [300000, 400000, 500000, 530000, 400000],
        "y": [200000, 300000, 400000, 180000, 150000],
    })


@pytest.fixture(scope="module")
def latlon_dataset() -> pl.DataFrame:
    # verified co-ords using qgis to transform those in the xy_dataset (epsg 27700 -> 4326)
    return pl.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "lon": [-3.448079, -2.001428, -0.494362, -0.128329, -2.001375],
        "lat": [51.689821, 52.597808, 53.487243, 51.503992, 51.249166],
    })


@pytest.fixture(scope="module")
def expected_refs() -> set:
    return {
        599424788162674687,
        599424878356987903,
        599423139968974847,
        599423697240981503,
        599424725885648895,
    }


@pytest.fixture(scope="module")
def expected_refs_list() -> list:
    return [
        599424788162674687,
        599424878356987903,
        599423139968974847,
        599423697240981503,
        599424725885648895,
    ]


class TestImportDataset:
    @pytest.fixture(scope="class")
    def test_files_path(self):
        return Path(__file__).parent / "fixture_data"

    def test_csv_returns_dataframe(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.csv")
        assert_frame_equal(df, xy_dataset)

    def test_csv_with_nondefault_separator_returns_dataframe(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy_semicolon.csv", separator=";")
        assert_frame_equal(df, xy_dataset)

    def test_parquet_returns_dataframe(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.parquet")
        assert_frame_equal(df, xy_dataset)

    def test_json_returns_dataframe(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.json")
        assert_frame_equal(df, xy_dataset)

    def test_ndjson_returns_dataframe(self, test_files_path, xy_dataset):
        df = core._import_dataset(test_files_path / "xy.ndjson")
        assert_frame_equal(df, xy_dataset)

    def test_file_doesnt_exist_raises_error(self, test_files_path):
        with pytest.raises(FileNotFoundError, match="Dataset not found: *"):
            core._import_dataset(test_files_path / "xy.unknown")

    def test_unknown_extension_raises_error(self, test_files_path):
        with pytest.raises(ValueError, match="Dataset file type is not valid, given *"):
            core._import_dataset(test_files_path / "xy.other")


class TestReadXYDataset:
    def test_xy_dataset_missing_x_raises_error(self, xy_dataset):
        with pytest.raises(ValueError, match="'x' or 'y' columns are not included in the dataset"):
            core._read_xy_dataset(xy_dataset, "x_value", "y", 27700)

    def test_xy_dataset_missing_y_raises_error(self, xy_dataset):
        with pytest.raises(ValueError, match="'x' or 'y' columns are not included in the dataset"):
            core._read_xy_dataset(xy_dataset, "x", "y_value", 27700)

    def test_xy_dataset_missing_x_and_y_raises_error(self, xy_dataset):
        with pytest.raises(ValueError, match="'x' or 'y' columns are not included in the dataset"):
            core._read_xy_dataset(xy_dataset, "x_value", "y_value", 27700)

    def test_xy_dataset_returned_as_wgs84(self, xy_dataset, latlon_dataset):
        df = core._read_xy_dataset(xy_dataset, "x", "y", 27700)
        assert_frame_equal(df, latlon_dataset)

    def test_latlon_dataset_returned_unchanged(self, latlon_dataset):
        df = core._read_xy_dataset(latlon_dataset, "lon", "lat", 4326)
        assert_frame_equal(df, latlon_dataset)

    def test_latlon_dataset_with_alt_col_names_returned_unchanged(
        self, latlon_dataset: pl.DataFrame
    ):
        latlon_dataset = latlon_dataset.with_columns(
            pl.col("lon").alias("longitude"), pl.col("lat").alias("latitude")
        )
        df = core._read_xy_dataset(latlon_dataset, "longitude", "latitude", 4326)
        latlon_dataset = latlon_dataset.drop("longitude", "latitude")
        assert_frame_equal(df, latlon_dataset)


class TestHexagonRefsForPoints:
    def test_points_generate_expected_size5_hexagons_in_df(self, latlon_dataset, expected_refs):
        expected_series = pl.Series(name="h3_ref", values=list(expected_refs))
        dataset, _ = core._get_hexagon_refs_for_points(latlon_dataset, 5)
        assert_series_equal(
            dataset.select("h3_ref").to_series(), expected_series, check_order=False
        )

    def test_input_df_retains_data(self, latlon_dataset):
        dataset, _ = core._get_hexagon_refs_for_points(latlon_dataset, 5)
        assert_frame_equal(dataset.drop("h3_ref"), latlon_dataset, check_row_order=False)

    def test_points_generate_expected_size5_hexagon_ref_set(self, latlon_dataset, expected_refs):
        _, hex_refs = core._get_hexagon_refs_for_points(latlon_dataset, 5)
        assert hex_refs == expected_refs

    def test_empty_data_generates_empty_set(self):
        expected = set()
        _, hex_refs = core._get_hexagon_refs_for_points(pl.DataFrame({"lat": [], "lon": []}), 5)
        assert hex_refs == expected

    def test_empty_data_generates_empty_df(self):
        expected_series = pl.Series(name="h3_ref")
        dataset, _ = core._get_hexagon_refs_for_points(pl.DataFrame({"lat": [], "lon": []}), 5)
        assert_series_equal(dataset.select("h3_ref").to_series(), expected_series)


class TestGetHexagonPolygons:
    @pytest.fixture(scope="class")
    def expected_polys(self, expected_refs_list):
        geoms = [
            Polygon([
                (-3.3757093714879454, 51.69820007993203),
                (-3.5053436422835813, 51.73272257423428),
                (-3.6080164502927823, 51.6811903909734),
                (-3.580861649240846, 51.59519769482759),
                (-3.451418266847575, 51.5607699427712),
                (-3.3489389047352387, 51.61224032577989),
                (-3.3757093714879454, 51.69820007993203),
            ]),
            Polygon([
                (-1.977650500683687, 52.57235895958127),
                (-1.8731921814750925, 52.621367868727255),
                (-1.8979033675108699, 52.706431776793714),
                (-2.027469268593714, 52.74252504465365),
                (-2.1321444680221098, 52.69345896993032),
                (-2.1070369270140694, 52.608356977038575),
                (-1.977650500683687, 52.57235895958127),
            ]),
            Polygon([
                (-0.6808060214522392, 53.45049792645889),
                (-0.5518632906529836, 53.413041720925044),
                (-0.4457610158490708, 53.45976141351786),
                (-0.4683625808633735, 53.54398956917154),
                (-0.5974718902105141, 53.581541219542665),
                (-0.7038130846587468, 53.534769084214794),
                (-0.6808060214522392, 53.45049792645889),
            ]),
            Polygon([
                (0.0542718130165512, 51.506311654843635),
                (-0.0692940978798558, 51.54399608943081),
                (-0.1717985446099623, 51.49597969639887),
                (-0.1505100096980458, 51.41032812299651),
                (-0.0270925498115125, 51.37274254089537),
                (0.0751848748771522, 51.42070984556818),
                (0.0542718130165512, 51.506311654843635),
            ]),
            Polygon([
                (-1.968314509613917, 51.31068650532574),
                (-2.0703877633842658, 51.26042861171404),
                (-2.0460074072834455, 51.174313502519816),
                (-1.9199305507519617, 51.13849732928368),
                (-1.8180641211005693, 51.1886990552312),
                (-1.8420676885992824, 51.27477294931256),
                (-1.968314509613917, 51.31068650532574),
            ]),
        ]
        return gpd.GeoDataFrame({"h3_ref": expected_refs_list}, geometry=geoms, crs="EPSG:4326")

    def test_empty_refs_set_generates_empty_df(self):
        assert_geodataframe_equal(
            core._get_hexagon_polygons(set()),
            gpd.GeoDataFrame({"h3_ref": []}, geometry=[], crs="EPSG:4326"),
        )

    def test_empty_refs_list_generates_empty_df(self):
        assert_geodataframe_equal(
            core._get_hexagon_polygons(list()),
            gpd.GeoDataFrame({"h3_ref": []}, geometry=[], crs="EPSG:4326"),
        )

    def test_expected_refs_generates_expected_geometries(self, expected_refs_list, expected_polys):
        assert_geodataframe_equal(
            core._get_hexagon_polygons(expected_refs_list), expected_polys, check_less_precise=True
        )


class TestGroupbyHexagons:
    @pytest.fixture(scope="class")
    def refs_for_grouping(self, expected_refs_list):
        return [
            expected_refs_list[0],
            expected_refs_list[0],
            expected_refs_list[1],
            expected_refs_list[1],
            expected_refs_list[1],
        ]

    @pytest.fixture(scope="class")
    def df_for_grouping(self, refs_for_grouping) -> pl.DataFrame:
        dummy_pop = pl.Series("population", [100, 200, 250, 250, 400])
        h3_ref = pl.Series("h3_ref", refs_for_grouping)
        return pl.DataFrame([h3_ref, dummy_pop])

    @pytest.fixture(scope="class")
    def expected_refs_grouped(self, expected_refs_list):
        return [expected_refs_list[0], expected_refs_list[1]]

    @pytest.fixture(scope="class")
    def expected_pops_summed(self):
        return [300, 900]

    @pytest.fixture(scope="class")
    def expected_pops_mean(self):
        return [150, 300]

    @pytest.fixture(scope="class")
    def expected_pops_median(self):
        return [150, 250]

    def test_empty_input_gives_empty_output(self):
        assert_frame_equal(
            core._groupby_hexagons(pl.DataFrame({"h3_ref": []})), pl.DataFrame({"h3_ref": []})
        )

    def test_wrong_h3_column_raises_error(self, df_for_grouping: pl.DataFrame):
        with pytest.raises(ValueError, match="h3_ref_field*"):
            core._groupby_hexagons(df_for_grouping, "wrong")

    def test_missing_aggregation_column_raises_error(self, df_for_grouping: pl.DataFrame):
        with pytest.raises(
            ValueError, match="some of the aggregations column names are missing from the input_df*"
        ):
            core._groupby_hexagons(df_for_grouping, temp={"column": "wrong", "agg": "sum"})

    def test_duplicate_aggregation_column_target_raises_error(self, df_for_grouping: pl.DataFrame):
        with pytest.raises(
            ValueError,
            match="some of the target aggregations column names are duplicates from input_df*",
        ):
            core._groupby_hexagons(df_for_grouping, h3_ref={"column": "population", "agg": "sum"})

    def test_no_aggregation_creates_expected_result(self, df_for_grouping, expected_refs_grouped):
        expected = pl.DataFrame({"h3_ref": expected_refs_grouped})
        assert_frame_equal(core._groupby_hexagons(df_for_grouping), expected, check_row_order=False)

    def test_simple_aggregation_creates_expected_result(
        self, df_for_grouping, expected_refs_grouped, expected_pops_summed
    ):
        expected = pl.DataFrame({
            "h3_ref": expected_refs_grouped,
            "population_sum": expected_pops_summed,
        })
        assert_frame_equal(
            core._groupby_hexagons(
                df_for_grouping, population_sum={"column": "population", "agg": "sum"}
            ),
            expected,
            check_row_order=False,
        )

    def test_many_aggregations_creates_expected_result(
        self,
        df_for_grouping,
        expected_refs_grouped,
        expected_pops_summed,
        expected_pops_mean,
        expected_pops_median,
    ):
        expected = pl.DataFrame({
            "h3_ref": expected_refs_grouped,
            "population_sum": expected_pops_summed,
            "population_mean": expected_pops_mean,
            "population_median": expected_pops_median,
        })
        assert_frame_equal(
            core._groupby_hexagons(
                df_for_grouping,
                population_sum={"column": "population", "agg": "sum"},
                population_mean={"column": "population", "agg": "mean"},
                population_median={"column": "population", "agg": "median"},
            ),
            expected,
            check_row_order=False,
            check_dtypes=False,
        )


# if __name__ == "__main__":
#     xy_dataset().write_csv(Path(__file__).parent / "fixture_data" / "xy.csv")
#     xy_dataset().write_csv(Path(__file__).parent / "fixture_data" / "xy_semicolon.csv", separator=";")
#     xy_dataset().write_parquet(Path(__file__).parent / "fixture_data" / "xy.parquet")
#     xy_dataset().write_ndjson(Path(__file__).parent / "fixture_data" / "xy.ndjson")
#     xy_dataset().write_json(Path(__file__).parent / "fixture_data" / "xy.json")
