# hats

A CLI tool for managing authentication context across multiple clients and projects. When working across many clients, it's easy to run commands against the wrong account — wrong git identity, wrong GCP project, wrong AWS profile. `hats` makes it easy to verify and switch your local tool authentication to match the client or project you're currently working on.

## Problem

When juggling multiple clients, your local tooling (git, `gcloud`, `aws`) each maintain their own auth state independently. Switching between client contexts means remembering to update all of them, and it's easy to miss one.

## Scope

This tool tracks and manages authentication/identity context for:

- **git** — user name and email (`git config --global`)
- **gcloud** — active account and project (`gcloud config`) _(planned)_
- **aws** — active profile (`AWS_PROFILE` / `~/.aws/config`) _(planned)_

## Usage

```
# Check current auth state
hats status

# Switch all tools to a named client/project context
hats use <client>

# List configured client contexts
hats list
```

## Configuration

Client contexts are defined in `~/.config/hats/config.toml`:

```toml
[clients.acme]
[clients.acme.git]
name = "Jane Smith"
email = "jane@acme.com"

[clients.personal]
[clients.personal.git]
name = "Jane Smith"
email = "jane@personal.dev"
```

## Requirements

- Python >= 3.13
- `git` installed and on `PATH`
- `gcloud` and `aws` CLIs (when those integrations are added)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```
