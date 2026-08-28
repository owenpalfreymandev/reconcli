
# Recon CLI

Recon is a powerful CLI companion for developers and tools for agents, turning GitHub activity and repository data into useful insights from your terminal.



[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![CI](https://github.com/owenpalfreymandev/reconcli/actions/workflows/ci.yml/badge.svg)](https://github.com/owenpalfreymandev/reconcli/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/recon-cli)](https://pypi.org/)
[![License](https://img.shields.io/github/license/owenpalfreymandev/reconcli)](https://github.com/owenpalfreymandev/reconcli/blob/main/LICENSE)
## Overview

Recon allows for developers to view basic GitHub analytics in the terminal quickly, rather than opening up their browser. This means it allows agents to interect with the service without having browser capabilities.

It is powered by [Typer](github.com/fastapi/typer), a library for building fast CLI tools, and made pretty by [Rich](https://github.com/textualize/rich) and it's prebuilt components.
## Features

* **GitHub Authentication** — Securely authenticate with GitHub using OAuth device flow.
* **User Information** — View information about your authenticated GitHub account.
* **Repository Explorer** — List and inspect GitHub repositories directly from the terminal.
* **Repository Statistics** — Explore repository languages, contributors, and other useful statistics.
* **Rich Terminal UI** — Clean, structured terminal output powered by Rich.
* **Fast CLI Workflow** — Quickly access GitHub information without leaving the command line.
* **Modular Architecture** — Built with reusable services and components to make Recon easy to maintain and extend.
* **Automated Testing** — Tested with an automated CI pipeline to help maintain reliability and code quality.

## Installation

Since we want you to be able to use Recon from anywhere - not just one directory - we recomend you install it with [uv package manager](https://docs.astral.sh/uv/getting-started/installation/).

```bash
  uv tool install recon-gh
```
For the best experience, then login to your GitHub account (this step is not strictly required).
```bash
    recon login
```
## Usage

Here you can learn how to get started with terminal commands, and learn how to find more.

### View Your GitHub Profile

The `me` command displays information about your authenticated GitHub account.

```bash
recon me
```

Example output:

```text
╭────── Owen Palfreyman ───────╮ ╭──────────────────────────────╮
│ Repositories  2              │ │                              │
│ Followers     7              │ │                              │
│ Following     2              │ │                              │
│ Location      United Kingdom │ │                              │
│ Company       —              │ │                              │
│ Joined        2023-11-02     │ │                              │
╰───── @owenpalfreymandev ─────╯ │                              │
                                 ╰──────────────────────────────╯
```

### Scout Another GitHub User

Use `scout` to explore another GitHub user's profile.

```bash
recon scout torvalds
```

Example output:

```text
╭──────── Linus Torvalds ────────╮ ╭──────────────────────────────╮
│ Repositories  12               │ │                              │
│ Followers     318572           │ │                              │
│ Following     0                │ │                              │
│ Location      Portland, OR     │ │                              │
│ Company       Linux Foundation │ │                              │
│ Joined        2011-09-03       │ │                              │
╰────────── @torvalds ───────────╯ │                              │
                                   ╰──────────────────────────────╯
```

### List Your Repositories

The `list` command displays your GitHub repositories.

```bash
recon list
```

This provides a quick way to see your repositories before using `details` to explore a specific project.

### Authentication

Recon uses GitHub's device flow for authentication.

To log in:

```bash
recon login
```

To log out:

```bash
recon logout
```

### Explore a Repository

The `details` command gives you an overview of a GitHub repository.

```bash
recon details owenpalfreymandev fpark
```

The command takes two arguments:

* `owner` — The GitHub username or organisation that owns the repository.
* `repo` — The name of the repository.

### Need Some Help?

Not sure what a command can do? Recon has built-in help for every command.

```bash
recon details --help
```

This shows you the available arguments and options for the command, including additional ways to get information from a repository.

```text
Usage: recon details [OPTIONS] {owner} {repo}

Gain insights into your repo

Arguments:
  owner    Repository owner, e.g. owenpalfreymandev
  repo     Repository name, e.g. reconcli

Options:
  --contributors    View contributors in more detail.
  --languages       View language usage in more detail.
  --help            Show this message and exit.
```

For example, the `--languages` option can be used to get a more detailed breakdown of the languages used in a repository:

```bash
recon details owenpalfreymandev fpark --languages
```

```text
╭──────────────────────────────────────────────────────────╮
│                        LANGUAGES                         │
│                 owenpalfreymandev/fpark                  │
╰──────────────────────────────────────────────────────────╯
4 languages returned by GitHub · 100% of reported code

LANGUAGE BREAKDOWN
──────────────────────────────────────────────────────────
1    TypeScript                        279.9 KB
    ████████████████████████████████  95.9%

2    PLpgSQL                             7.0 KB
    █                                 2.4%

3    CSS                                 4.3 KB
    █                                 1.5%

4    JavaScript                           559 B
    █                                 0.2%
──────────────────────────────────────────────────────────
Showing all 4 languages
```


### Explore Further

These are just some of the commands available in Recon. There are plenty more options to play with, with more commands and features coming soon. Check the [roadmap](https://github.com/owenpalfreymandev/reconcli/blob/main/README.md) for more details.

## Contributing

Contributions are always welcome!

To clone the repo and download all dependencies, run:
```bash
git clone https://github.com/owenpalfreymandev/reconcli.git
uv sync
```

You can run unit tests and type tests with:
```bash
uv run pytest
uv run pyright
```

Be sure to lint before commiting, or it will fail CI/CD:
```bash
uv run ruff check --fix .
```

### Workflow

A basic workflow to follow is:

1. Fork the repository
2. Create a branch
3. Make changes
4. Run tests/lint/type checks
5. Open a PR
## License

Recon is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
## Author

Recon is developed by Owen Palfreyman.

GitHub: @owenpalfreymandev
Repository: owenpalfreymandev/reconcli

*or could could just run `recon details owenpalfreymandev reconcli --contributors` wink wink*
