from pathlib import Path

import tomllib

CONFIG_PATH = Path("~/.config/hats/config.toml").expanduser()


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


def get_client(name: str) -> dict:
    config = load_config()
    clients = config.get("clients", {})
    if name not in clients:
        available = ", ".join(clients.keys()) if clients else "(none)"
        raise KeyError(f"Client '{name}' not found. Available: {available}")
    return clients[name]
