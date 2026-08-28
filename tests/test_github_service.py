from unittest.mock import Mock

import pytest

import app.services.github as github


def token_headers(monkeypatch):
    monkeypatch.setattr(github, "get_token", lambda: "token")
    return {
        "Authorization": "Bearer token",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }


def http_response(status, data, *, headers=None):
    response = Mock()
    response.status_code = status
    response.ok = 200 <= status < 400
    response.json.return_value = data
    response.headers = headers or {}
    response.reason = "error"
    response.text = "error"
    return response


@pytest.mark.parametrize(
    "function,args,path,data",
    [
        ("get_repo_details", ("o", "r"), "/repos/o/r", {"id": 1}),
        ("get_languages", ("o", "r"), "/repos/o/r/languages", {"Python": 10}),
        ("get_user", ("a user",), "/users/a%20user", {"login": "a user"}),
        ("get_user_repos", (), "/user/repos", [{"name": "r"}]),
    ],
)
def test_basic_github_requests(monkeypatch, function, args, path, data):
    headers = token_headers(monkeypatch)
    response = http_response(200, data)
    request = Mock(return_value=response)
    monkeypatch.setattr(github.requests, "get", request)

    assert getattr(github, function)(*args) == data
    request.assert_called_once_with(
        github.GITHUB_API + path, headers=headers, timeout=10
    )


def test_get_user_rejects_empty_username():
    with pytest.raises(ValueError, match="must not be empty"):
        github.get_user("")


def test_non_2xx_uses_github_error(monkeypatch):
    token_headers(monkeypatch)
    monkeypatch.setattr(
        github.requests,
        "get",
        Mock(return_value=http_response(404, {"message": "missing"})),
    )
    with pytest.raises(RuntimeError, match="missing"):
        github.get_languages("o", "r")


def stats_response(status, data):
    return http_response(status, data)


def test_top_contributors_filters_sorts_limits_and_finds_current_user(monkeypatch):
    token_headers(monkeypatch)
    data = [
        {"author": {"login": "Low", "html_url": "l", "avatar_url": "la"}, "total": 2},
        {"author": None, "total": 99},
        {"author": {"login": "HIGH", "html_url": "h", "avatar_url": "ha"}, "total": 8},
        {"author": {"login": "Mid", "html_url": "m", "avatar_url": "ma"}, "total": 5},
    ]
    monkeypatch.setattr(
        github.requests, "get", Mock(return_value=stats_response(200, data))
    )
    result = github.get_top_contributors(
        "o", "r", limit=2, current_login="high", include_metadata=True
    )
    assert [row["login"] for row in result.contributors] == ["HIGH", "Mid"]
    assert result.total_contributors == 3
    assert result.total_commits == 15
    assert result.current_contributor["login"] == "HIGH"


def test_top_contributors_202_then_200(monkeypatch):
    token_headers(monkeypatch)
    request = Mock(side_effect=[stats_response(202, {}), stats_response(200, [])])
    monkeypatch.setattr(github.requests, "get", request)
    monkeypatch.setattr(github.time, "sleep", Mock())
    assert github.get_top_contributors("o", "r") == []
    assert request.call_count == 2


def test_top_contributors_still_computing(monkeypatch):
    token_headers(monkeypatch)
    monkeypatch.setattr(
        github.requests, "get", Mock(return_value=stats_response(202, {}))
    )
    monkeypatch.setattr(github.time, "sleep", Mock())
    with pytest.raises(RuntimeError, match="still computing"):
        github.get_top_contributors("o", "r")


def test_top_contributors_plain_list_and_no_current_match(monkeypatch):
    token_headers(monkeypatch)
    data = [{"author": {"login": "A", "html_url": "", "avatar_url": ""}, "total": 1}]
    monkeypatch.setattr(
        github.requests, "get", Mock(return_value=stats_response(200, data))
    )
    assert isinstance(github.get_top_contributors("o", "r"), list)
    result = github.get_top_contributors(
        "o", "r", current_login="other", include_metadata=True
    )
    assert result.current_contributor is None
