import subprocess
from unittest.mock import Mock

from app.services import local_credentials

# Captured before conftest's autouse fixture stubs discovery out.
REAL_DISCOVER = local_credentials.discover


def git_result(returncode=0, stdout=""):
    return subprocess.CompletedProcess(
        args=["git"], returncode=returncode, stdout=stdout
    )


def test_from_env_reads_both_variables(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "one")
    monkeypatch.setenv("GITHUB_TOKEN", " two ")
    credentials = local_credentials.from_env()
    assert [(c.source, c.token) for c in credentials] == [
        ("env:GH_TOKEN", "one"),
        ("env:GITHUB_TOKEN", "two"),
    ]


def test_from_env_ignores_blank(monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_TOKEN", "  ")
    assert local_credentials.from_env() == []


def test_from_gh_cli(monkeypatch):
    monkeypatch.setattr(local_credentials.gh_cli, "get_token", lambda: "gho_token")
    credential = local_credentials.from_gh_cli()
    assert credential is not None
    assert credential.source == "gh_cli"
    assert credential.token == "gho_token"


def test_git_credential_helper_reads_password_without_prompting(monkeypatch):
    run = Mock(
        return_value=git_result(
            stdout="protocol=https\nhost=github.com\nusername=octo\npassword=gho_x\n"
        )
    )
    monkeypatch.setattr(local_credentials.subprocess, "run", run)

    credential = local_credentials.from_git_credential_helper()

    assert credential is not None
    assert credential.token == "gho_x"
    assert run.call_args.kwargs["env"]["GIT_TERMINAL_PROMPT"] == "0"
    assert "host=github.com" in run.call_args.kwargs["input"]


def test_git_credential_helper_failures_return_none(monkeypatch):
    for result in (
        git_result(returncode=128),
        git_result(stdout="protocol=https\nhost=github.com\n"),
    ):
        monkeypatch.setattr(
            local_credentials.subprocess, "run", Mock(return_value=result)
        )
        assert local_credentials.from_git_credential_helper() is None

    for error in (subprocess.TimeoutExpired(cmd="git", timeout=10), OSError()):
        monkeypatch.setattr(
            local_credentials.subprocess, "run", Mock(side_effect=error)
        )
        assert local_credentials.from_git_credential_helper() is None


def test_discover_orders_sources_and_drops_duplicate_tokens(monkeypatch):
    gh = local_credentials.Credential("gh_cli", "GitHub CLI (gh)", "same")
    env = local_credentials.Credential("env:GH_TOKEN", "$GH_TOKEN", "same")
    git = local_credentials.Credential("git_credential", "git", "other")
    monkeypatch.setattr(local_credentials, "from_gh_cli", lambda: gh)
    monkeypatch.setattr(local_credentials, "from_env", lambda: [env])
    monkeypatch.setattr(local_credentials, "from_git_credential_helper", lambda: git)

    assert REAL_DISCOVER() == [gh, git]
