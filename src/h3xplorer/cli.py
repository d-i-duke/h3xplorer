"""Console script for h3xplorer."""

import click


@click.version_option(package_name="h3xplorer")
@click.command()
def cli(args=None):
    """Console script for h3xplorer."""
    click.echo("Replace this message by putting your code into h3xplorer.cli.cli")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0
