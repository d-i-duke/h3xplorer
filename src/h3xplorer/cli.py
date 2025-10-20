"""Console script for h3xplorer."""

from pathlib import Path

import click

from h3xplorer.core import xy_plot


@click.version_option(package_name="h3xplorer")
@click.group()
def cli(args=None):
    """Welcome to h3xplorer, a hexagon-based spatial data exploration package."""
    return 0


@cli.command()
@click.option(
    "--data-file", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("--x-field", required=True, type=click.STRING)
@click.option("--y-field", required=True, type=click.STRING)
@click.option("--crs", required=True, type=click.INT)
@click.option("--hex-size", required=True, type=click.IntRange(0, 15))
@click.option("--agg-field", required=True, type=click.STRING)
@click.option("--agg-type", required=True, type=click.STRING)
@click.option(
    "--outfile", required=True, type=click.Path(dir_okay=False, writable=True, path_type=Path)
)
def plot_xy_data(data_file, x_field, y_field, crs, hex_size, agg_field, agg_type, outfile) -> None:
    """Aggregates xy-based data and then plots this to an HTML file in a standard format."""
    xy_plot(data_file, x_field, y_field, crs, hex_size, agg_field, agg_type, outfile)
