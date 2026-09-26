import pytest

from app.services import auth, gh_cli, local_credentials, storage


@pytest.fixture(autouse=True)
def isolated_gh_cli(monkeypatch):
    """
    Keep tests away from the developer's real `gh` install.

    Tests that exercise the GitHub CLI path re-patch these with their own stubs.
    """
    gh_cli.reset_cache()
    monkeypatch.setattr(gh_cli, "is_installed", lambda: False)
    monkeypatch.setattr(gh_cli, "get_token", lambda: None)
    # Never search the developer's real environment or git credential helper,
    # and never prompt: tests opt in to the interactive flow explicitly.
    monkeypatch.setattr(local_credentials, "discover", list)
    monkeypatch.setattr(auth, "is_interactive", lambda: False)


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    """Keep tests from reading or writing the developer's real ~/.atlas config."""
    atlas_dir = tmp_path / ".atlas"
    monkeypatch.setattr(storage, "ATLAS_DIR", atlas_dir)
    monkeypatch.setattr(storage, "CONFIG_FILE", atlas_dir / "config.json")
