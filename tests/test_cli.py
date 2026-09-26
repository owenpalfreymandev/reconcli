from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


def test_cli_has_expected_commands():
    """Sanity check that all top-level commands are registered on the Typer app."""
    expected_commands = {"login", "logout", "me", "scout", "list", "details"}
    registered_names = {command.name for command in app.registered_commands}

    assert expected_commands <= registered_names


def test_cli_has_no_unexpected_commands():
    """Catches accidental duplicate/renamed commands as the CLI grows."""
    expected_commands = {"login", "logout", "me", "scout", "list", "details"}
    registered_names = {command.name for command in app.registered_commands}

    assert registered_names == expected_commands


def test_help_is_available_as_short_flag():
    for argv in (["-h"], ["--help"], ["login", "-h"]):
        result = runner.invoke(app, argv)
        assert result.exit_code == 0, argv
        assert "Usage:" in result.output


def test_bare_invocation_lists_commands():
    result = runner.invoke(app, [])
    assert "login" in result.output
    assert "details" in result.output
