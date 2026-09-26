import json
from pathlib import Path

ATLAS_DIR = Path.home() / ".atlas"
CONFIG_FILE = ATLAS_DIR / "config.json"

TOKEN_KEY = "github_token"
CLIENT_ID_KEY = "github_client_id"
CREDENTIAL_SOURCE_KEY = "credential_source"


def _read_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    return data if isinstance(data, dict) else {}


def _write_config(data: dict):
    ATLAS_DIR.mkdir(exist_ok=True)

    CONFIG_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")


def _set_value(key: str, value):
    data = _read_config()

    data[key] = value

    _write_config(data)


def _clear_value(key: str):
    data = _read_config()

    if key not in data:
        return

    del data[key]

    if data:
        _write_config(data)
    elif CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


def save_token(token: str):
    _set_value(TOKEN_KEY, token)


def get_token():
    return _read_config().get(TOKEN_KEY)


def clear_token():
    _clear_value(TOKEN_KEY)


def save_client_id(client_id: str):
    """Persist an OAuth app client ID so future logins do not need --client-id."""
    _set_value(CLIENT_ID_KEY, client_id)


def get_client_id():
    return _read_config().get(CLIENT_ID_KEY)


def save_credential_source(source: str):
    """Record that the user allowed Recon to use an external login, such as gh."""
    _set_value(CREDENTIAL_SOURCE_KEY, source)


def get_credential_source():
    return _read_config().get(CREDENTIAL_SOURCE_KEY)


def clear_credential_source():
    _clear_value(CREDENTIAL_SOURCE_KEY)
