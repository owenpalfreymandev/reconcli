import time
from dataclasses import dataclass
from urllib.parse import quote

import requests

from app.services import gh_cli, storage
from app.services.github_errors import (
    github_headers,
    raise_for_github_error,
)

GITHUB_API = "https://api.github.com"

TOP_CONTRIBUTORS = 10
STATS_POLL_ATTEMPTS = 5
STATS_POLL_INTERVAL_SECONDS = 1


@dataclass
class ContributorResults:
    """Top contributor rows plus metadata from GitHub's statistics response."""

    contributors: list[dict[str, str | int | None]]
    total_contributors: int
    total_commits: int
    current_contributor: dict[str, str | int | None] | None = None


NOT_AUTHENTICATED_MESSAGE = (
    "Not authenticated with GitHub. Run `recon login`, which can reuse a login "
    "already on this machine, such as the GitHub CLI's."
)


def resolve_token():
    """
    Prefer a token saved by `recon login`, then the GitHub CLI login, but only
    if the user allowed Recon to use it.
    """
    token = storage.get_token()

    if token:
        return token

    if storage.get_credential_source() == gh_cli.SOURCE:
        return gh_cli.get_token()

    return None


def _get_auth_headers():
    token = resolve_token()

    if not token:
        raise RuntimeError(NOT_AUTHENTICATED_MESSAGE)

    return github_headers(token)


def get_authenticated_user():
    response = requests.get(
        f"{GITHUB_API}/user",
        headers=_get_auth_headers(),
        timeout=10,
    )

    raise_for_github_error(response)

    return response.json()


def get_user(username: str):
    """Return a GitHub user's public profile."""
    if not username:
        raise ValueError("username must not be empty")

    response = requests.get(
        f"{GITHUB_API}/users/{quote(username, safe='')}",
        headers=_get_auth_headers(),
        timeout=10,
    )

    raise_for_github_error(response)

    return response.json()


def get_user_repos():
    response = requests.get(
        f"{GITHUB_API}/user/repos",
        headers=_get_auth_headers(),
        timeout=10,
    )

    raise_for_github_error(response)

    return response.json()


def get_repo_details(owner: str, repo: str):
    response = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}",
        headers=_get_auth_headers(),
        timeout=10,
    )

    raise_for_github_error(response)

    return response.json()


def get_languages(owner: str, repo: str):
    response = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/languages",
        headers=_get_auth_headers(),
        timeout=10,
    )

    raise_for_github_error(response)

    return response.json()


def get_top_contributors(
    owner: str,
    repo: str,
    limit: int = TOP_CONTRIBUTORS,
    current_login: str | None = None,
    include_metadata: bool = False,
) -> list[dict[str, str | int | None]] | ContributorResults:
    """
    Return contributors ranked by commit count.

    GitHub may return 202 while it calculates statistics,
    so we retry until the data is available.
    """

    if limit < 1:
        raise ValueError("limit must be at least 1")

    url = f"{GITHUB_API}/repos/{owner}/{repo}/stats/contributors"

    for attempt in range(STATS_POLL_ATTEMPTS):
        response = requests.get(
            url,
            headers=_get_auth_headers(),
            timeout=10,
        )

        if response.status_code == 202:
            if attempt < STATS_POLL_ATTEMPTS - 1:
                time.sleep(STATS_POLL_INTERVAL_SECONDS)
                continue

            raise RuntimeError(
                "GitHub is still computing contributor statistics. Try again shortly."
            )

        raise_for_github_error(response)

        statistics = [
            contributor
            for contributor in response.json()
            if contributor.get("author") is not None
        ]
        contributors = sorted(
            statistics,
            key=lambda contributor: contributor["total"],
            reverse=True,
        )

        def format_contributor(contributor: dict) -> dict[str, str | int | None]:
            author = contributor["author"]
            return {
                "login": author["login"],
                "commits": contributor["total"],
                "profile_url": author["html_url"],
                "avatar_url": author["avatar_url"],
            }

        current_contributor = next(
            (
                format_contributor(contributor)
                for contributor in contributors
                if current_login
                and contributor["author"]["login"].casefold()
                == current_login.casefold()
            ),
            None,
        )

        top_contributors = [
            format_contributor(contributor) for contributor in contributors[:limit]
        ]
        if not include_metadata:
            return top_contributors

        return ContributorResults(
            contributors=top_contributors,
            total_contributors=len(contributors),
            total_commits=sum(contributor["total"] for contributor in contributors),
            current_contributor=current_contributor,
        )

    return ContributorResults([], 0, 0) if include_metadata else []
