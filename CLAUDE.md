# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`hats` is a CLI tool for switching authentication context (git identity, gcloud account/project, AWS profile) between named client/project configurations. See README.md for the intended command interface.

The package name is `hats`. Module structure:
- `hats/main.py` — CLI entrypoint (typer app), entrypoint `hats.main:main` registered in `pyproject.toml`
- `hats/config.py` — config loading from `~/.config/hats/config.toml`
- `hats/tools/git.py` — git identity management

**Current implementation status:** git is implemented. gcloud and aws are planned but not yet built.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Python 3.13 is required (see `.python-version`).

## Running

```bash
hats status
hats list
hats use <client>
```

Or during development before installing:

```bash
python -m hats.main
```

## Configuration

Client contexts are stored in `~/.config/hats/config.toml`. Each context defines identity/auth settings per tool (git, gcloud, aws).

## External tools managed

- **git** — `git config --global` for user name/email (implemented)
- **gcloud** — `gcloud config` for active account and project (planned)
- **aws** — `~/.aws/config` profiles / `AWS_PROFILE` (planned)

## Notes

- `hats status` currently shows git identity only; it will expand as gcloud/aws are added.
- The CLI framework is `typer`. Config format is TOML with a `[clients.<name>]` structure.
- The README references `~/.config/local-tool-management/config.toml` — the actual path used in code is `~/.config/hats/config.toml`.
