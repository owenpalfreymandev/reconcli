import typer

from app.ui.display import display_user

app = typer.Typer()


@app.command()
def me():
    """Get information about me!"""
    from app.services.github import get_authenticated_user

    user = get_authenticated_user()
    display_user(user)

@app.command()
def scout(user: str):
    """Scout another GitHub user."""
    from app.services.github import get_user

    profile = get_user(user)
    display_user(profile)
