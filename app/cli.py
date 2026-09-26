import functools

import typer

from app.commands import auth, me, repo

# Click inherits help_option_names into subcommands, so `-h` works everywhere.
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)


def friendly_errors(command):
    """
    Report expected failures as a message rather than a traceback.

    Services raise RuntimeError for things the user can act on, such as missing
    credentials, so those should read as advice instead of a crash.
    """

    @functools.wraps(command)
    def wrapper(*args, **kwargs):
        try:
            return command(*args, **kwargs)
        except RuntimeError as error:
            typer.secho(str(error), fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1) from error

    return wrapper


def register(name: str, command):
    app.command(name=name)(friendly_errors(command))


# Commands that can be ran in the CLI
register("login", auth.login)
register("logout", auth.logout)
register("me", me.me)
register("scout", me.scout)
register("list", repo.list)
register("details", repo.details)
