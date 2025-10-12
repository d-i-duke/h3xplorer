"""Console script for h3xplorer."""

import click


@click.version_option(package_name="h3xplorer")
@click.command()
def cli(args=None):
    """Console script for h3xplorer."""
    click.echo("Welcome to h3xplorer, a hexagon-based spatial data exploration package.")
    return 0


@click.command()
def plot_xy_data():
    """Aggregates xy-based data and then plots this to an HTML file."""
