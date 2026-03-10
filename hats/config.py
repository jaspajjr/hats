from pathlib import Path

import tomllib
import tomli_w

CONFIG_PATH = Path("~/.config/hats/config.toml").expanduser()


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


def _save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("wb") as f:
        tomli_w.dump(config, f)


def get_client(name: str) -> dict:
    config = load_config()
    clients = config.get("clients", {})
    if name not in clients:
        available = ", ".join(clients.keys()) if clients else "(none)"
        raise KeyError(f"Client '{name}' not found. Available: {available}")
    return clients[name]


def create_client(name: str, data: dict) -> None:
    config = load_config()
    clients = config.setdefault("clients", {})
    if name in clients:
        raise KeyError(f"Client '{name}' already exists.")
    clients[name] = data
    _save_config(config)


def update_client(name: str, data: dict) -> None:
    config = load_config()
    clients = config.setdefault("clients", {})
    if name not in clients:
        available = ", ".join(clients.keys()) if clients else "(none)"
        raise KeyError(f"Client '{name}' not found. Available: {available}")
    clients[name] = data
    _save_config(config)


def delete_client(name: str) -> None:
    config = load_config()
    clients = config.get("clients", {})
    if name not in clients:
        available = ", ".join(clients.keys()) if clients else "(none)"
        raise KeyError(f"Client '{name}' not found. Available: {available}")
    del clients[name]
    _save_config(config)
