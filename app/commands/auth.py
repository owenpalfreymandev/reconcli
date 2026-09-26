import typer

from app.services import auth

app = typer.Typer()


@app.command()
def login(
    client_id: str = typer.Option(
        None,
        "--client-id",
        help="GitHub OAuth app client ID for the device flow (saved for next time). "
        "Skips the GitHub CLI.",
    ),
    token: str = typer.Option(
        None,
        "--token",
        help="Log in with a personal access token instead of the device flow.",
    ),
):
    """Login to GitHub, reusing an existing GitHub CLI login when there is one."""
    auth.login(client_id=client_id, token=token)


@app.command()
def logout():
    """Logout of GitHub. Does not touch your GitHub CLI login."""
    auth.logout()
