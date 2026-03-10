from typing import Optional

import typer

from hats import config as cfg
from hats.tools import git

app = typer.Typer()


def _parse_fields(git_name: Optional[str], git_email: Optional[str]) -> dict:
    data = {}
    if git_name is not None or git_email is not None:
        git_cfg = {}
        if git_name is not None:
            git_cfg["name"] = git_name
        if git_email is not None:
            git_cfg["email"] = git_email
        data["git"] = git_cfg
    return data


@app.command()
def list():
    """List available client contexts."""
    conf = cfg.load_config()
    clients = conf.get("clients", {})
    if not clients:
        typer.echo("No clients configured.")
        return
    for name in clients:
        typer.echo(name)


@app.command()
def status():
    """Show current git identity."""
    info = git.get_status()
    typer.echo(f"name:  {info['name'] or '(not set)'}")
    typer.echo(f"email: {info['email'] or '(not set)'}")


@app.command()
def use(client: str):
    """Switch to a named client context."""
    try:
        client_cfg = cfg.get_client(client)
    except KeyError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)

    git_cfg = client_cfg.get("git", {})
    if git_cfg:
        git.apply(git_cfg)
        typer.echo(f"Switched to '{client}'.")
        typer.echo(f"  git name:  {git_cfg.get('name', '(unchanged)')}")
        typer.echo(f"  git email: {git_cfg.get('email', '(unchanged)')}")
    else:
        typer.echo(f"No git config for client '{client}'.")


@app.command()
def show(client: str):
    """Show configuration for a named client."""
    try:
        client_cfg = cfg.get_client(client)
    except KeyError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    git_cfg = client_cfg.get("git", {})
    typer.echo(f"[{client}]")
    if git_cfg:
        typer.echo(f"  git name:  {git_cfg.get('name', '(not set)')}")
        typer.echo(f"  git email: {git_cfg.get('email', '(not set)')}")
    else:
        typer.echo("  (no settings)")


@app.command()
def create(
    client: str,
    git_name: Optional[str] = typer.Option(None, "--git-name", help="Git user.name"),
    git_email: Optional[str] = typer.Option(None, "--git-email", help="Git user.email"),
):
    """Create a new client context."""
    data = _parse_fields(git_name, git_email)
    try:
        cfg.create_client(client, data)
    except KeyError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    typer.echo(f"Created client '{client}'.")


@app.command()
def update(
    client: str,
    git_name: Optional[str] = typer.Option(None, "--git-name", help="Git user.name"),
    git_email: Optional[str] = typer.Option(None, "--git-email", help="Git user.email"),
):
    """Update an existing client context (replaces its settings)."""
    data = _parse_fields(git_name, git_email)
    try:
        cfg.update_client(client, data)
    except KeyError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    typer.echo(f"Updated client '{client}'.")


@app.command()
def delete(
    client: str,
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete a client context."""
    if not yes:
        typer.confirm(f"Delete client '{client}'?", abort=True)
    try:
        cfg.delete_client(client)
    except KeyError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    typer.echo(f"Deleted client '{client}'.")


def main():
    app()
