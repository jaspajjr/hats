# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`hats` is a CLI tool for switching authentication context (git identity, gcloud account/project, AWS profile) between named client/project configurations. See README.md for the intended command interface.

Written in Rust. Module structure:
- `src/main.rs` — CLI entrypoint and command handlers (clap)
- `src/config.rs` — config loading/saving from `~/.config/hats/config.toml`
- `src/git.rs` — git identity management

**Current implementation status:** git is implemented. gcloud and aws are planned but not yet built.

## Setup

```bash
cargo build
```

## Running

```bash
cargo run -- status
cargo run -- list
cargo run -- use <client>
```

Or after installing the binary:

```bash
hats status
hats list
hats use <client>
```

## Configuration

Client contexts are stored in `~/.config/hats/config.toml`. Each context defines identity/auth settings per tool (git, gcloud, aws).

## External tools managed

- **git** — `git config --global` for user name/email (implemented)
- **gcloud** — `gcloud config` for active account and project (planned)
- **aws** — `~/.aws/config` profiles / `AWS_PROFILE` (planned)

## Notes

- `hats status` currently shows git identity only; it will expand as gcloud/aws are added.
- The CLI framework is `clap` with derive macros. Config format is TOML with a `[clients.<name>]` structure.
