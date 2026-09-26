from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def build_repository_table(repositories: list[dict]) -> Table:
    """Build the compact repository listing used by ``recon list``."""
    table_width = _repository_table_width()
    repository_width = max(13, min(32, table_width - 66))
    table = Table(
        title=f"Repositories ({len(repositories)})",
        title_style="bold cyan",
        header_style="bold cyan",
        box=None,
        show_edge=False,
        pad_edge=False,
        padding=(0, 1),
        collapse_padding=False,
        width=table_width,
    )
    table.add_column(
        "Repository",
        no_wrap=True,
        overflow="ellipsis",
        width=repository_width,
        max_width=repository_width,
    )
    table.add_column(
        "Visibility", no_wrap=True, overflow="ellipsis", width=10, max_width=10
    )
    table.add_column(
        "Language", no_wrap=True, overflow="ellipsis", width=9, max_width=9
    )
    table.add_column(
        "Updated", no_wrap=True, overflow="ellipsis", width=10, max_width=10
    )
    table.add_column("Branch", no_wrap=True, overflow="ellipsis", width=6, max_width=6)
    table.add_column("Stars", justify="right", no_wrap=True, width=5)
    table.add_column("Forks", justify="right", no_wrap=True, width=5)
    table.add_column("Issues", justify="right", no_wrap=True, width=5)

    for repository in repositories:
        visibility = repository.get("visibility") or (
            "private" if repository.get("private") else "public"
        )
        table.add_row(
            str(repository.get("full_name") or repository.get("name") or "—"),
            str(visibility or "—"),
            str(repository.get("language") or "—"),
            _format_updated(repository.get("updated_at")),
            str(repository.get("default_branch") or "—"),
            _format_count(repository.get("stargazers_count")),
            _format_count(repository.get("forks_count")),
            _format_count(repository.get("open_issues_count")),
        )

    if not repositories:
        table.add_row("No repositories found.", *["—"] * 7)

    return table


def display_repository_list(
    repositories: list[dict], username: str, boxy: bool = False
) -> None:
    """Render a compact, scan-friendly table of repositories."""
    width = _repository_box_width() if boxy else _repository_table_width()
    console.print(build_view_header("List", username, width=width))
    if boxy:
        for repository in repositories:
            console.print(build_repository_panel(repository))
        if not repositories:
            console.print(Panel("No repositories found.", width=width))
        return
    console.print(build_repository_table(repositories))


def build_repository_panel(repository: dict) -> Panel:
    """Build the box-style repository summary used by ``recon list --boxy``."""
    from app.commands.repo import format_topics

    visibility = repository.get("visibility") or (
        "private" if repository.get("private") else "public"
    )
    language = repository.get("language") or "—"
    branch = repository.get("default_branch") or "—"
    topics = repository.get("topics") or []
    topic_text = (
        format_topics([str(topic) for topic in topics]).replace(", ", " · ")
        if topics
        else "—"
    )
    content = Text()
    content.append(
        f"{str(visibility).capitalize()} · {language} · {branch}\n",
        style="cyan",
    )
    content.append(
        f"Stars {_format_count(repository.get('stargazers_count'))}   "
        f"Forks {_format_count(repository.get('forks_count'))}   "
        f"Issues {_format_count(repository.get('open_issues_count'))}\n"
    )
    content.append(topic_text, style="dim")
    return Panel(
        content,
        title=str(repository.get("full_name") or repository.get("name") or "—"),
        width=_repository_box_width(),
        border_style="cyan",
    )


def _repository_table_width() -> int:
    """Calculate the shared width for the list table and header."""
    return min(max(1, console.width - 1), 98)


def _repository_box_width() -> int:
    """Calculate the narrower width used by boxy repository summaries."""
    return min(max(1, console.width - 1), 72)


def _format_count(value: object) -> str:
    """Format repository counters while keeping missing values predictable."""
    if value is None:
        return "0"
    return f"{value:,}" if isinstance(value, int) else str(value)


def _format_updated(value: object) -> str:
    """Show the date portion of GitHub's ISO timestamp."""
    if not value:
        return "—"
    return str(value).split("T", 1)[0]


def build_view_header(title: str, subtitle: str, width: int = 60) -> Panel:
    """Create the shared header used by focused repository views."""
    content = Text(justify="center")
    content.append(title.upper(), style="bold cyan")
    content.append("\n")
    content.append(subtitle, style="bold")
    return Panel(content, width=width, border_style="cyan")


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


def format_bytes(size: int | None) -> str:
    """Format byte size values for display."""
    if size is None:
        return "Not available"

    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    current_unit = 0

    while value >= 1000 and current_unit < len(units) - 1:
        value /= 1000
        current_unit += 1

    if current_unit == 0:
        return f"{int(value)} B"
    return f"{value:.1f} {units[current_unit]}"


def display_repo_details(
    details: dict,
    languages: dict[str, int],
    contributions: list[dict],
):
    """Display a repository overview."""

    full_name = details.get("full_name", "Unknown repository")
    description = details.get("description") or "No description provided."
    visibility = details.get("visibility") or (
        "private" if details.get("private") else "public"
    )
    url = details.get("html_url") or "—"

    header_panel = build_view_header("Details", full_name)

    # Contributions
    contribution_table = Table(
        show_header=False,
        box=None,
        pad_edge=False,
        padding=(0, 1),
    )

    contribution_table.add_column("Contributor")
    contribution_table.add_column("Commits", justify="right")
    contribution_table.add_column("Share", justify="right")

    ranked_contributions = contributions[:5]
    if ranked_contributions:
        total_commits = sum(
            int(contributor.get("commits") or 0) for contributor in ranked_contributions
        )
        for index, contributor in enumerate(ranked_contributions):
            commits = int(contributor.get("commits") or 0)
            percentage = commits / total_commits * 100 if total_commits else 0
            contribution_table.add_row(
                str(contributor.get("login") or "Unknown"),
                _format_count(commits),
                _overview_bar_label(
                    percentage, spaced=index < len(ranked_contributions) - 1
                ),
            )
    else:
        contribution_table.add_row(
            "No contributor data",
            "—",
            "",
        )
    for _ in range(len(ranked_contributions) if ranked_contributions else 1, 5):
        contribution_table.add_row("", "", "")

    contributions_panel = Panel(
        contribution_table,
        title="Contributors",
        expand=False,
        border_style="cyan",
    )

    # Languages
    language_table = Table(
        show_header=False,
        box=None,
        pad_edge=False,
        expand=True,
        padding=(0, 1),
    )

    language_table.add_column("Language")
    language_table.add_column("Usage", justify="right")

    if not languages:
        language_table.add_row("No language data returned.", "")
    else:
        total_bytes = sum(languages.values())
        ranked_languages = sorted(
            languages.items(), key=lambda item: item[1], reverse=True
        )[:5]
        for index, (language, byte_count) in enumerate(ranked_languages):
            percentage = byte_count / total_bytes * 100 if total_bytes else 0
            language_table.add_row(
                language,
                _overview_bar_label(
                    percentage, spaced=index < len(ranked_languages) - 1
                ),
            )
        for _ in range(min(len(languages), 5), 5):
            language_table.add_row("", "")
    if not languages:
        for _ in range(1, 5):
            language_table.add_row("", "")

    languages_panel = Panel(
        language_table,
        title="Languages",
        expand=False,
        border_style="cyan",
    )

    repository = Table(show_header=False, box=None, pad_edge=False, expand=True)
    repository.add_column("Label", style="dim", no_wrap=True)
    repository.add_column("Value", overflow="fold")
    repository.add_row("Description", description)
    repository.add_row("Visibility", visibility.capitalize())
    repository.add_row("URL", url)
    repository.add_row("★ Stars", str(details.get("stargazers_count") or 0))
    repository.add_row("⑂ Forks", str(details.get("forks_count") or 0))
    repository.add_row("! Issues", str(details.get("open_issues_count") or 0))
    repository.add_row("Size", format_size(details.get("size")))
    repository_panel = Panel(
        repository,
        title="Repository",
        border_style="cyan",
        width=60,
    )

    console.print(header_panel)
    console.print()
    console.print(
        Columns(
            [contributions_panel, languages_panel],
            expand=False,
            equal=True,
            padding=(0, 0),
        )
    )
    console.print()
    console.print(repository_panel)


def _progress_bar(percentage: float, width: int = 12) -> str:
    """Build a compact proportional bar for overview panels."""
    filled = round(max(0, min(100, percentage)) / 100 * width)
    return f"[green]{'█' * filled}[/green]"


def _overview_bar_label(percentage: float, spaced: bool = True) -> str:
    """Render an overview bar with a compact line of breathing room."""
    suffix = "\n" if spaced else ""
    return f"{_progress_bar(percentage)} {percentage:.1f}%{suffix}"


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

    console.print(
        Text(
            f"{total_contributors} contributors returned by GitHub · showing top {shown_count}",
            style="dim",
        )
    )

    current_is_ranked = any(
        current_login and contributor["login"].casefold() == current_login.casefold()
        for contributor in contributors
    )
    largest_count = max(contributor["commits"] for contributor in contributors)

    if current_contributor and not current_is_ranked:
        console.print()
        console.print(Text("YOUR CONTRIBUTION", style="bold cyan"))
        console.print(Text("─" * 58, style="dim"))
        console.print(
            _contributor_row(
                current_contributor,
                total_commits,
                largest_count,
                marker="● ",
                highlight=True,
            )
        )

    console.print()
    console.print(Text("TOP CONTRIBUTORS", style="bold"))
    console.print(Text("─" * 58, style="dim"))
    for rank, contributor in enumerate(contributors, start=1):
        is_current_user = bool(
            current_login
            and contributor["login"].casefold() == current_login.casefold()
        )
        console.print(
            _contributor_row(
                contributor,
                total_commits,
                largest_count,
                rank=rank,
                marker="● " if is_current_user else "  ",
                highlight=is_current_user,
            )
        )
        if rank < shown_count:
            console.print()

    console.print(Text("─" * 58, style="dim"))
    console.print(
        Text(
            f"Showing {shown_count} of {total_contributors} contributors returned by GitHub",
            style="dim",
        )
    )


def display_languages(full_name: str, languages: dict[str, int]) -> None:
    """Display all languages reported by GitHub with proportional usage bars."""
    display_view_header("Languages", full_name)

    if not languages:
        console.print(Text("No language data returned.", style="dim"))
        return

    total_bytes = sum(languages.values())
    ranked_languages = sorted(
        languages.items(),
        key=lambda language: language[1],
        reverse=True,
    )
    largest_count = ranked_languages[0][1]
    language_count = len(ranked_languages)

    console.print(
        Text(
            f"{language_count} languages returned by GitHub · 100% of reported code",
            style="dim",
        )
    )
    console.print()
    console.print(Text("LANGUAGE BREAKDOWN", style="bold"))
    console.print(Text("─" * 58, style="dim"))

    for index, (language, byte_count) in enumerate(ranked_languages, start=1):
        console.print(
            _language_row(
                language,
                byte_count,
                total_bytes,
                largest_count,
                rank=index,
            )
        )
        if index < language_count:
            console.print()

    console.print(Text("─" * 58, style="dim"))
    console.print(Text(f"Showing all {language_count} languages", style="dim"))


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
    filled = (
        max(1, round(commits / largest_count * bar_width))
        if commits and largest_count
        else 0
    )
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


def _language_row(
    language: str,
    byte_count: int,
    total_bytes: int,
    largest_count: int,
    rank: int | None = None,
) -> Text:
    """Build one compact language row with a proportional usage bar."""
    percentage = byte_count / total_bytes * 100 if total_bytes else 0
    bar_width = 32
    filled = (
        max(1, round(byte_count / largest_count * bar_width))
        if byte_count and largest_count
        else 0
    )
    bar = "█" * filled

    row = Text()
    if rank is not None:
        row.append(f"{rank:<2} ", style="dim")
    row.append("  ", style="dim")
    row.append(f"{language:<30}")
    row.append(f"{format_bytes(byte_count):>12}\n")
    row.append(" " * (4 if rank is not None else 3))
    row.append(bar.ljust(bar_width), style="green")
    row.append(f"  {percentage:.1f}%", style="dim")
    return row
