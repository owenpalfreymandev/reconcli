from app.cli import app


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