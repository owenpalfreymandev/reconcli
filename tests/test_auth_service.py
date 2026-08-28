from unittest.mock import Mock

import pytest

import app.services.auth as auth


def test_login_requires_client_id(monkeypatch):
    monkeypatch.setattr(auth, "CLIENT_ID", None)
    with pytest.raises(RuntimeError, match="Missing GITHUB_CLIENT_ID"):
        auth.login()


def test_poll_for_token_returns_immediately(monkeypatch):
    monkeypatch.setattr(auth.requests, "post", Mock(return_value=Mock(json=lambda: {"access_token": "tok"})))
    assert auth.poll_for_token({"device_code": "code"}) == "tok"


def test_poll_for_token_retries_pending(monkeypatch):
    post = Mock(side_effect=[Mock(json=lambda: {"error": "authorization_pending"}), Mock(json=lambda: {"access_token": "tok"})])
    sleep = Mock()
    monkeypatch.setattr(auth.requests, "post", post)
    monkeypatch.setattr(auth.time, "sleep", sleep)
    assert auth.poll_for_token({"device_code": "code", "interval": 2}) == "tok"
    sleep.assert_called_once_with(2)


def test_poll_for_token_other_error_raises(monkeypatch):
    monkeypatch.setattr(auth.requests, "post", Mock(return_value=Mock(json=lambda: {"error": "expired_token"})))
    with pytest.raises(RuntimeError, match="expired_token"):
        auth.poll_for_token({"device_code": "code"})


def test_logout_clears_token(monkeypatch):
    clear = Mock()
    monkeypatch.setattr(auth, "clear_token", clear)
    auth.logout()
    clear.assert_called_once_with()
