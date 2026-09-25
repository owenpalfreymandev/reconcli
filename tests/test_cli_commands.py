from unittest.mock import Mock

from typer.testing import CliRunner

from app.cli import app
from app.commands import auth as auth_command
from app.commands import me as me_command
from app.ui.repo import build_repository_table

runner = CliRunner()


def test_login_logout_delegate(monkeypatch):
    login, logout = Mock(), Mock()
    monkeypatch.setattr(auth_command.auth, "login", login)
    monkeypatch.setattr(auth_command.auth, "logout", logout)
    assert runner.invoke(app, ["login"]).exit_code == 0
    assert runner.invoke(app, ["logout"]).exit_code == 0
    login.assert_called_once_with()
    logout.assert_called_once_with()


def user():
    return {
        "login": "octo",
        "name": "Octo",
        "public_repos": 1,
        "followers": 2,
        "following": 3,
        "created_at": "2020-01-01T00:00:00Z",
    }


def test_me_and_scout_display_user(monkeypatch):
    get_me, get_user, display = (
        Mock(return_value=user()),
        Mock(return_value=user()),
        Mock(),
    )
    monkeypatch.setattr("app.services.github.get_authenticated_user", get_me)
    monkeypatch.setattr("app.services.github.get_user", get_user)
    monkeypatch.setattr(me_command, "display_user", display)
    assert runner.invoke(app, ["me"]).exit_code == 0
    assert runner.invoke(app, ["scout", "octo"]).exit_code == 0
    get_me.assert_called_once_with()
    get_user.assert_called_once_with("octo")
    assert display.call_count == 2


def test_list_handles_empty_and_missing_optional_fields(monkeypatch):
    repo = {"full_name": "o/r", "html_url": "https://github.com/o/r"}
    monkeypatch.setattr(
        "app.services.github.get_authenticated_user",
        Mock(return_value={"login": "octo"}),
    )
    monkeypatch.setattr(
        "app.services.github.get_user_repos", Mock(side_effect=[[], [repo]])
    )
    assert runner.invoke(app, ["list"]).exit_code == 0
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "o/r" in result.output
    assert "LIST" in result.output
    assert "octo" in result.output
    assert "Repositories (1)" in result.output
    assert "—" in result.output


def test_list_renders_repository_columns(monkeypatch):
    monkeypatch.setattr(
        "app.services.github.get_authenticated_user",
        Mock(return_value={"login": "octo"}),
    )
    monkeypatch.setattr(
        "app.services.github.get_user_repos",
        Mock(
            return_value=[
                {
                    "full_name": "octo/a-really-long-repository-name",
                    "visibility": "public",
                    "language": "Python",
                    "updated_at": "2026-09-25T12:34:56Z",
                    "default_branch": "main",
                    "stargazers_count": 1_234,
                    "forks_count": 56,
                    "open_issues_count": 7,
                }
            ]
        ),
    )

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert [column.header for column in build_repository_table([{}]).columns] == [
        "Repository",
        "Visibility",
        "Language",
        "Updated",
        "Branch",
        "Stars",
        "Forks",
        "Issues",
    ]
    assert "1,234" in result.output
    assert "2026-09-25" in result.output
    assert "Visibility" in result.output
    assert "Language" in result.output


def test_list_boxy_renders_repository_panels(monkeypatch):
    monkeypatch.setattr(
        "app.services.github.get_authenticated_user",
        Mock(return_value={"login": "octo"}),
    )
    monkeypatch.setattr(
        "app.services.github.get_user_repos",
        Mock(
            return_value=[
                {
                    "full_name": "octo/reconcli",
                    "visibility": "public",
                    "language": "Python",
                    "default_branch": "main",
                    "stargazers_count": 0,
                    "forks_count": 0,
                    "open_issues_count": 0,
                    "topics": [
                        "cli",
                        "developer-tools",
                        "github",
                        "python",
                        "rich-cli",
                        "terminal",
                    ],
                }
            ]
        ),
    )

    result = runner.invoke(app, ["list", "--boxy"])

    assert result.exit_code == 0
    assert "LIST" in result.output
    assert "octo/reconcli" in result.output
    assert "Public · Python · main" in result.output
    assert "Stars 0   Forks 0   Issues 0" in result.output
    assert (
        "cli · developer-tools · github · python · rich-cli + 1 more..."
        in result.output
    )
    assert "Repositories (" not in result.output
    assert result.output.count("─" * 70) >= 2


def test_details_rejects_both_views():
    result = runner.invoke(app, ["details", "o", "r", "--contributors", "--languages"])
    assert result.exit_code != 0
    assert "Choose either" in result.output


def test_details_default_calls_services_and_prints(monkeypatch):
    details = {"full_name": "o/r", "description": "desc", "size": 1}
    monkeypatch.setattr(
        "app.services.github.get_repo_details", Mock(return_value=details)
    )
    monkeypatch.setattr(
        "app.services.github.get_languages", Mock(return_value={"Python": 1})
    )
    monkeypatch.setattr(
        "app.services.github.get_top_contributors", Mock(return_value=[])
    )
    result = runner.invoke(app, ["details", "o", "r"])
    assert result.exit_code == 0
    assert "Repository" in result.output
    assert "Languages" in result.output
