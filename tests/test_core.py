"""Tests for `h3xplorer` core."""

from pathlib import Path

import geopandas as gpd
import pytest
from shapely import Polygon

from h3xplorer.core import xy_plot


@pytest.fixture(scope="module")
def expected_refs_list_nodupes() -> list:
    return [599424788162674687, 599423139968974847, 599423697240981503, 599424725885648895]


@pytest.fixture(scope="module")
def expected_geoms():
    return [
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


@pytest.fixture(scope="module")
def expected_polys(expected_refs_list_nodupes, expected_geoms):
    return gpd.GeoDataFrame(
        {"h3_ref": expected_refs_list_nodupes}, geometry=expected_geoms, crs="EPSG:4326"
    )


class TestXYPlot:
    @pytest.fixture(scope="class")
    def test_files_path(self):
        return Path(__file__).parent / "fixture_data"

    def test_standard_input_generates_expected_map(self, test_files_path):
        expected_str = 'Map(basemap_style=<CartoBasemap.DarkMatter: \'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json\'>, custom_attribution=\'\', layers=(PolygonLayer(get_fill_color=arro3.core.ChunkedArray<FixedSizeList(Field { name: "", data_type: UInt8, nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }, 4)>\n[\n  [\n    [167, 143, 8, 191],\n  ]\n]\n, get_line_color=arro3.core.ChunkedArray<FixedSizeList(Field { name: "", data_type: UInt8, nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }, 4)>\n[\n  [\n    [167, 143, 8, 229],\n  ]\n]\n, get_line_width=5.0, line_width_max_pixels=5.0, line_width_min_pixels=2.0, table=arro3.core.Table\n+---------+--------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+\n| id_mean | h3_ref             | geometry                                                                                                                                                                                                                                                                                                                                           |\n| UInt8   | Int64              | List(Field { name: "", data_type: List(Field { name: "vertices", data_type: FixedSizeList(Field { name: "xy", data_type: Float64, nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }, 2), nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }), nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }) |\n+---------+--------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+\n| 3       | 576918149140578303 | [[[5.523646549290303, 55.70676846515228], [-10.444977544778336, 63.09505407752544], [-29.882335644494077, 58.03211375817634], [-27.492923060366778, 46.76027724369226], [-12.384126872990429, 40.869133191665526], [2.026568965384605, 45.18424868970644], [5.523646549290303, 55.70676846515228]]]                                                |\n+---------+--------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+),), layout=Layout(height=\'100%\', width=\'100%\'), show_tooltip=True, view_state=ViewState(longitude=-9.590071579809202, latitude=52.193480555867225, zoom=3, pitch=0, bearing=0))'
        result = xy_plot(
            data_file=test_files_path / "xy.parquet",
            x_field="x",
            y_field="y",
            crs=27700,
            hex_size=0,
            agg_field="id",
            agg_type="mean",
        )
        assert str(result) == expected_str
