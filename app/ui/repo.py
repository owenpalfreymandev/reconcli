from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def display_repo_details(
    details: dict,
    languages: list[str],
    contributions: list[dict],
):
    """Display a repository overview."""

    full_name = details.get("full_name", "Unknown repository")
    description = details.get("description") or "No description provided."
    visibility = details.get("visibility") or (
        "private" if details.get("private") else "public"
    )
    primary_language = details.get("language") or "—"
    url = details.get("html_url") or "—"

    # Repository header
    header = Text()
    header.append(full_name, style="bold")
    header.append("\n")
    header.append(description, style="dim")
    header.append("\n\n")
    header.append(visibility.capitalize(), style="cyan")
    header.append("    ")
    header.append(primary_language, style="green")

    header_panel = Panel(
        header,
        title="Repository",
        expand=False,
    )

    # Statistics
    stats = Table(
        show_header=False,
        box=None,
        pad_edge=False,
    )

    stats.add_column("Metric", style="dim")
    stats.add_column("Value", justify="right")

    stats.add_row(
        "★ Stars",
        str(details.get("stargazers_count") or 0),
    )
    stats.add_row(
        "⑂ Forks",
        str(details.get("forks_count") or 0),
    )
    stats.add_row(
        "! Issues",
        str(details.get("open_issues_count") or 0),
    )
    stats.add_row(
        "Size",
        details.get("formatted_size", "—"),
    )

    stats_panel = Panel(
        stats,
        title="Statistics",
        expand=False,
    )

    # Contributions
    contribution_table = Table(
        show_header=False,
        box=None,
        pad_edge=False,
    )

    contribution_table.add_column("Contributor")
    contribution_table.add_column("Commits", justify="right")

    if contributions:
        for contributor in contributions:
            contribution_table.add_row(
                contributor["login"],
                str(contributor["commits"]),
            )
    else:
        contribution_table.add_row(
            "No contributor data",
            "—",
        )

    contributions_panel = Panel(
        contribution_table,
        title="Contributions",
        expand=False,
    )

    # Languages
    language_table = Table(
        show_header=False,
        box=None,
        pad_edge=False,
    )

    language_table.add_column("Language")
    language_table.add_column("Usage")

    for language in languages:
        language_name, percentage = language.split(": ")
        language_table.add_row(
            language_name,
            percentage,
        )

    languages_panel = Panel(
        language_table,
        title="Languages",
        expand=False,
    )

    console.print(header_panel)

    console.print(
        Columns(
            [stats_panel, contributions_panel],
            expand=False,
            equal=True,
        )
    )

    console.print(languages_panel)

    console.print(
        Text(
            f"↗ {url}",
            style="dim",
        )
    )
