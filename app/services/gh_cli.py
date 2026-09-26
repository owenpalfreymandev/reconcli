"""Read credentials from the GitHub CLI (`gh`) so Recon can reuse existing logins."""

import shutil
import subprocess

GH_EXECUTABLE = "gh"
HOSTNAME = "github.com"
SOURCE = "gh_cli"
TIMEOUT_SECONDS = 10


def is_installed() -> bool:
    return shutil.which(GH_EXECUTABLE) is not None


def _run(*args: str) -> str | None:
    """Run a gh subcommand, returning stripped stdout or None if it is unusable."""
    if not is_installed():
        return None

    try:
        result = subprocess.run(
            [GH_EXECUTABLE, *args],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if result.returncode != 0:
        return None

    output = result.stdout.strip()

    return output or None


_token_cache: dict[str, str | None] = {}


def get_token() -> str | None:
    """Return the token `gh` is logged in with, or None if it is not usable."""
    if "token" not in _token_cache:
        _token_cache["token"] = _run("auth", "token", "--hostname", HOSTNAME)

    return _token_cache["token"]


def reset_cache():
    """Forget the cached token. Mostly useful in tests."""
    _token_cache.clear()
