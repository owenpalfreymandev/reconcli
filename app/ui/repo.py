from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text

console = Console()


def build_view_header(title: str, subtitle: str) -> Panel:
    """Create the shared header used by focused repository views."""
    content = Text(justify="center")
    content.append(title.upper(), style="bold cyan")
    content.append("\n")
    content.append(subtitle, style="bold")
    return Panel(content, width=60, border_style="cyan")


def display_view_header(title: str, subtitle: str) -> None:
    """Render the shared header used by focused repository views."""
    console.print(build_view_header(title, subtitle))


def format_size(size: int | None) -> str:
    # Format GitHub's repository size value for display.
    if size is None:
        return "Not available"

    units = ["KB", "MB", "GB", "TB", "PB"]
    value = size
    current_unit = 0

    while value >= 1000 and current_unit < len(units) - 1:
        value /= 1000
        current_unit += 1

    return f"{value:.1f} {units[current_unit]}"


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

    header_panel = build_view_header("Details", full_name)

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
        format_size(details.get("size")),
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
    console.print(Text(description, style="dim"))
    console.print(
        Text.assemble(
            (visibility.capitalize(), "cyan"),
            ("    "),
            (primary_language, "green"),
        )
    )
    console.print()

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


def display_contributors(
    full_name: str,
    contributors: list[dict],
    total_contributors: int,
    total_commits: int,
    current_login: str | None = None,
    current_contributor: dict | None = None,
):
    """Display a focused view of GitHub contributor statistics."""
    display_view_header("Contributors", full_name)

    shown_count = len(contributors)
    if not total_contributors:
        console.print(Text("No contributor data returned.", style="dim"))
        return

    console.print(Text(
        f"{total_contributors} contributors returned by GitHub · showing top {shown_count}",
        style="dim",
    ))

    current_is_ranked = any(
        current_login and contributor["login"].casefold() == current_login.casefold()
        for contributor in contributors
    )
    largest_count = max(contributor["commits"] for contributor in contributors)

    if current_contributor and not current_is_ranked:
        console.print()
        console.print(Text("YOUR CONTRIBUTION", style="bold cyan"))
        console.print(Text("─" * 58, style="dim"))
        console.print(_contributor_row(
            current_contributor, total_commits, largest_count,
            marker="● ", highlight=True,
        ))

    console.print()
    console.print(Text("TOP CONTRIBUTORS", style="bold"))
    console.print(Text("─" * 58, style="dim"))
    for rank, contributor in enumerate(contributors, start=1):
        is_current_user = bool(
            current_login and contributor["login"].casefold() == current_login.casefold()
        )
        console.print(_contributor_row(
            contributor, total_commits, largest_count, rank=rank,
            marker="● " if is_current_user else "  ", highlight=is_current_user,
        ))
        if rank < shown_count:
            console.print()

    console.print(Text("─" * 58, style="dim"))
    console.print(Text(
        f"Showing {shown_count} of {total_contributors} contributors returned by GitHub",
        style="dim",
    ))


def _contributor_row(
    contributor: dict,
    total_commits: int,
    largest_count: int,
    rank: int | None = None,
    marker: str = "",
    highlight: bool = False,
) -> Text:
    """Build one compact contributor row with a proportional contribution bar."""
    commits = int(contributor.get("commits") or 0)
    percentage = commits / total_commits * 100 if total_commits else 0
    bar_width = 32
    filled = max(1, round(commits / largest_count * bar_width)) if commits and largest_count else 0
    bar = "█" * filled
    username_style = "bold cyan" if highlight else ""
    bar_style = "cyan" if highlight else "green"
    commit_label = "commit" if commits == 1 else "commits"

    row = Text()
    if rank is not None:
        row.append(f"{rank:<2} ", style="dim")
    row.append(marker, style="cyan" if highlight else "dim")
    row.append(f"{contributor.get('login', 'Unknown'):<30}", style=username_style)
    row.append(f"{commits:>6} {commit_label}\n")
    row.append(" " * (4 if rank is not None else 3))
    row.append(bar.ljust(bar_width), style=bar_style)
    row.append(f"  {percentage:.1f}%", style="dim")
    return row
