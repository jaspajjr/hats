import subprocess


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", "config", "--global", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_status() -> dict:
    try:
        name = _git("user.name")
    except subprocess.CalledProcessError:
        name = None
    try:
        email = _git("user.email")
    except subprocess.CalledProcessError:
        email = None
    return {"name": name, "email": email}


def apply(config: dict) -> None:
    name = config.get("name")
    email = config.get("email")
    if name:
        _git("user.name", name)
    if email:
        _git("user.email", email)
