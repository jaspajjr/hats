import typer

from hats import config as cfg
from hats.tools import git

app = typer.Typer()


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


def main():
    app()
