import pytest
from requests import Response

from app.services.github_errors import github_headers, raise_for_github_error


def response(status=500, *, ok=None, json_data=None, text="", reason="Server Error", headers=None):
    result = Response()
    result.status_code = status
    result._content = text.encode()
    result.reason = reason
    result.headers.update(headers or {})
    if ok is not None:
        result._content = b"{}"
    if json_data is not None:
        import json
        result._content = json.dumps(json_data).encode()
    return result


def test_github_headers():
    assert github_headers("abc") == {
        "Authorization": "Bearer abc",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }


def test_success_is_ignored():
    raise_for_github_error(response(200, ok=True))


def test_json_error_message_and_request_id():
    with pytest.raises(RuntimeError, match="Nope.*request ID: req-1"):
        raise_for_github_error(response(404, json_data={"message": "Nope"}, headers={"X-GitHub-Request-Id": "req-1"}))


def test_non_json_falls_back_to_text_then_reason():
    with pytest.raises(RuntimeError, match="plain text"):
        raise_for_github_error(response(500, text="plain text"))
    with pytest.raises(RuntimeError, match="Bad Gateway"):
        raise_for_github_error(response(500, reason="Bad Gateway"))


def test_request_id_is_omitted_when_absent():
    with pytest.raises(RuntimeError) as error:
        raise_for_github_error(response(404, json_data={"message": "missing"}))
    assert "request ID" not in str(error.value)


@pytest.mark.parametrize("status", [403, 429])
def test_rate_limit_details(status):
    with pytest.raises(RuntimeError) as error:
        raise_for_github_error(response(status, json_data={"message": "rate"}, headers={"X-RateLimit-Remaining": "0", "Retry-After": "3"}))
    assert "rate limit exhausted" in str(error.value)
    assert "retry after 3 seconds" in str(error.value)


@pytest.mark.parametrize("status", [404, 500])
def test_non_rate_limited_errors_have_no_rate_limit_text(status):
    with pytest.raises(RuntimeError) as error:
        raise_for_github_error(response(status, json_data={"message": "error"}))
    assert "rate limit" not in str(error.value)
