"""Tests for `h3xplorer` CLI."""

from click.testing import CliRunner

from h3xplorer import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 2  # because this is a group, it will technically error when called.
    assert "Welcome to h3xplorer" in result.output
    help_result = runner.invoke(cli.cli, ["--help"])
    assert help_result.exit_code == 0
    assert (
        "Welcome to h3xplorer, a hexagon-based spatial data exploration package.\n\nOptions:\n  "
        "--version  Show the version and exit.\n  "
        "--help     Show this message and exit.\n" in help_result.output
    )
