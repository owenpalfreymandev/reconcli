from builtins import list as builtins_list
from typing import cast

import typer

app = typer.Typer()

units = ["KB", "MB", "GB", "TB", "PB"]


def format_topics(topics: list[str], max_topics: int = 5) -> str:
    shown = topics[:max_topics]
    remaining = len(topics) - len(shown)
    rendered = ", ".join(shown)
    if remaining > 0:
        rendered = f"{rendered} + {remaining} more..."
    return rendered


def format_description(description: str, max_chars: int = 90) -> str:
    if len(description) <= max_chars:
        return description

    # Truncate at or after max_chars, but never in the middle of a word.
    cutoff = description.find(" ", max_chars)
    if cutoff == -1:
        cutoff = max_chars

    shown = description[:cutoff].rstrip()
    return f"{shown}..."


def format_size(size: int) -> str:
    units = ["KB", "MB", "GB", "TB", "PB"]

    current_unit = 0
    scaled_size: float = size

    while scaled_size >= 1000 and current_unit < len(units) - 1:
        scaled_size = scaled_size / 1000
        current_unit += 1

    return f"{scaled_size:.1f} {units[current_unit]}"


def format_languages(languages: dict[str, int], max_languages: int = 5) -> list[str]:
    if not languages:
        return ["No language data returned."]

    total_bytes = sum(languages.values())

    sorted_languages = sorted(languages.items(), key=lambda item: item[1], reverse=True)

    shown = sorted_languages[:max_languages]
    remaining = len(sorted_languages) - len(shown)

    formatted = []

    for language, byte_count in shown:
        percent = (byte_count / total_bytes * 100) if total_bytes else 0
        formatted.append(f"{language}: {percent:.1f}%")

    if remaining > 0:
        formatted.append(f"+ {remaining} more...")

    return formatted


@app.command()
def list(
    boxy: bool = typer.Option(
        False,
        "--boxy",
        help="Render each repository as a panel (not recommended for long lists).",
    ),
):
    """See a list of all your repos."""
    from app.services.github import get_authenticated_user, get_user_repos
    from app.ui.repo import display_repository_list

    user = get_authenticated_user()
    repos = get_user_repos()
    display_repository_list(
        repos,
        user.get("login", "Unknown user"),
        boxy=boxy,
    )


@app.command()
def details(
    owner: str = typer.Argument(..., help="Repository owner, e.g. owenpalfreymandev"),
    repo: str = typer.Argument(..., help="Repository name, e.g. reconcli"),
    contributors: bool = typer.Option(False, help="View contributors in more detail."),
    languages: bool = typer.Option(False, help="View language usage in more detail."),
):
    """Gain insights into your repo"""
    if contributors and languages:
        raise typer.BadParameter("Choose either --contributors or --languages.")

    from app.services.github import (
        ContributorResults,
        get_authenticated_user,
        get_languages,
        get_repo_details,
        get_top_contributors,
    )

    details = get_repo_details(owner, repo)

    if languages:
        from app.ui.repo import display_languages

        display_languages(
            details.get("full_name", f"{owner}/{repo}"),
            get_languages(owner, repo),
        )
        return

    if contributors:
        from app.ui.repo import display_contributors

        try:
            authenticated_user = get_authenticated_user()
        except RuntimeError:
            # Contributor statistics remain useful when GitHub cannot identify
            # the token owner for this request.
            authenticated_user = {}
        results = cast(
            ContributorResults,
            get_top_contributors(
                owner,
                repo,
                limit=5,
                current_login=authenticated_user.get("login"),
                include_metadata=True,
            ),
        )
        display_contributors(
            details.get("full_name", f"{owner}/{repo}"),
            results.contributors,
            results.total_contributors,
            results.total_commits,
            authenticated_user.get("login"),
            results.current_contributor,
        )
        return

    language_data = get_languages(owner, repo)
    contributions = cast(
        builtins_list[dict[str, str | int | None]],
        get_top_contributors(owner, repo, limit=5),
    )

    from app.ui.repo import display_repo_details

    display_repo_details(details, language_data, contributions)
