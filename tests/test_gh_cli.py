import subprocess
from unittest.mock import Mock

import pytest

from app.services import gh_cli

# Captured before conftest's autouse fixture stubs the module out.
REAL_GET_TOKEN = gh_cli.get_token
REAL_IS_INSTALLED = gh_cli.is_installed


@pytest.fixture(autouse=True)
def real_gh_cli(monkeypatch):
    """Undo the global stubbing so these tests exercise the real subprocess wrapper."""
    monkeypatch.setattr(gh_cli, "get_token", REAL_GET_TOKEN)
    monkeypatch.setattr(gh_cli, "is_installed", REAL_IS_INSTALLED)
    gh_cli.reset_cache()


def completed(returncode=0, stdout=""):
    return subprocess.CompletedProcess(
        args=["gh"], returncode=returncode, stdout=stdout
    )


def install_gh(monkeypatch, result):
    monkeypatch.setattr(gh_cli.shutil, "which", lambda _: "/usr/bin/gh")
    run = (
        Mock(side_effect=result)
        if isinstance(result, Exception)
        else Mock(return_value=result)
    )
    monkeypatch.setattr(gh_cli.subprocess, "run", run)
    return run


def test_returns_none_when_gh_missing(monkeypatch):
    monkeypatch.setattr(gh_cli.shutil, "which", lambda _: None)
    monkeypatch.setattr(gh_cli.subprocess, "run", Mock(side_effect=AssertionError))
    assert gh_cli.is_installed() is False
    assert gh_cli.get_token() is None


def test_returns_token_when_logged_in(monkeypatch):
    run = install_gh(monkeypatch, completed(stdout="gho_token\n"))
    assert gh_cli.get_token() == "gho_token"
    assert run.call_args.args[0] == ["gh", "auth", "token", "--hostname", "github.com"]


def test_token_is_cached(monkeypatch):
    run = install_gh(monkeypatch, completed(stdout="gho_token\n"))
    gh_cli.get_token()
    gh_cli.get_token()
    assert run.call_count == 1


def test_returns_none_when_not_logged_in(monkeypatch):
    install_gh(monkeypatch, completed(returncode=1))
    assert gh_cli.get_token() is None


def test_returns_none_on_empty_output(monkeypatch):
    install_gh(monkeypatch, completed(stdout="\n"))
    assert gh_cli.get_token() is None


def test_returns_none_when_gh_times_out(monkeypatch):
    install_gh(monkeypatch, subprocess.TimeoutExpired(cmd="gh", timeout=10))
    assert gh_cli.get_token() is None
