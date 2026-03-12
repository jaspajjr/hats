from typing import Optional

import typer

from hats import config as cfg
from hats.tools import git, gcloud

app = typer.Typer()


def _parse_fields(
    git_name: Optional[str],
    git_email: Optional[str],
    gcloud_account: Optional[str],
    gcloud_project: Optional[str],
) -> dict:
    data = {}
    if git_name is not None or git_email is not None:
        git_cfg = {}
        if git_name is not None:
            git_cfg["name"] = git_name
        if git_email is not None:
            git_cfg["email"] = git_email
        data["git"] = git_cfg
    if gcloud_account is not None or gcloud_project is not None:
        gcloud_cfg = {}
        if gcloud_account is not None:
            gcloud_cfg["account"] = gcloud_account
        if gcloud_project is not None:
            gcloud_cfg["project"] = gcloud_project
        data["gcloud"] = gcloud_cfg
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
    """Show current git identity and gcloud context."""
    git_info = git.get_status()
    typer.echo("git:")
    typer.echo(f"  name:  {git_info['name'] or '(not set)'}")
    typer.echo(f"  email: {git_info['email'] or '(not set)'}")
    typer.echo("gcloud:")
    try:
        gcloud_info = gcloud.get_status()
        typer.echo(f"  account: {gcloud_info['account'] or '(not set)'}")
        typer.echo(f"  project: {gcloud_info['project'] or '(not set)'}")
    except FileNotFoundError:
        typer.echo("  (gcloud not installed)")


@app.command()
def use(client: str):
    """Switch to a named client context."""
    try:
        client_cfg = cfg.get_client(client)
    except KeyError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)

    git_cfg = client_cfg.get("git", {})
    gcloud_cfg = client_cfg.get("gcloud", {})

    if not git_cfg and not gcloud_cfg:
        typer.echo(f"No config for client '{client}'.")
        return

    typer.echo(f"Switched to '{client}'.")
    if git_cfg:
        git.apply(git_cfg)
        typer.echo(f"  git name:  {git_cfg.get('name', '(unchanged)')}")
        typer.echo(f"  git email: {git_cfg.get('email', '(unchanged)')}")
    if gcloud_cfg:
        try:
            gcloud.apply(gcloud_cfg)
            typer.echo(f"  gcloud account: {gcloud_cfg.get('account', '(unchanged)')}")
            typer.echo(f"  gcloud project: {gcloud_cfg.get('project', '(unchanged)')}")
        except FileNotFoundError:
            typer.echo("  gcloud: not installed — skipping", err=True)


@app.command()
def show(client: str):
    """Show configuration for a named client."""
    try:
        client_cfg = cfg.get_client(client)
    except KeyError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    git_cfg = client_cfg.get("git", {})
    gcloud_cfg = client_cfg.get("gcloud", {})
    typer.echo(f"[{client}]")
    if not git_cfg and not gcloud_cfg:
        typer.echo("  (no settings)")
        return
    if git_cfg:
        typer.echo(f"  git name:  {git_cfg.get('name', '(not set)')}")
        typer.echo(f"  git email: {git_cfg.get('email', '(not set)')}")
    if gcloud_cfg:
        typer.echo(f"  gcloud account: {gcloud_cfg.get('account', '(not set)')}")
        typer.echo(f"  gcloud project: {gcloud_cfg.get('project', '(not set)')}")


@app.command()
def create(
    client: str,
    git_name: Optional[str] = typer.Option(None, "--git-name", help="Git user.name"),
    git_email: Optional[str] = typer.Option(None, "--git-email", help="Git user.email"),
    gcloud_account: Optional[str] = typer.Option(None, "--gcloud-account", help="gcloud active account"),
    gcloud_project: Optional[str] = typer.Option(None, "--gcloud-project", help="gcloud active project"),
):
    """Create a new client context."""
    data = _parse_fields(git_name, git_email, gcloud_account, gcloud_project)
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
    gcloud_account: Optional[str] = typer.Option(None, "--gcloud-account", help="gcloud active account"),
    gcloud_project: Optional[str] = typer.Option(None, "--gcloud-project", help="gcloud active project"),
):
    """Update an existing client context (replaces its settings)."""
    data = _parse_fields(git_name, git_email, gcloud_account, gcloud_project)
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
