import subprocess


def _gcloud(*args: str) -> str:
    result = subprocess.run(
        ["gcloud", "config", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_status() -> dict:
    try:
        account = _gcloud("get-value", "account")
        account = account if account != "(unset)" else None
    except subprocess.CalledProcessError:
        account = None
    try:
        project = _gcloud("get-value", "project")
        project = project if project != "(unset)" else None
    except subprocess.CalledProcessError:
        project = None
    return {"account": account, "project": project}


def apply(config: dict) -> None:
    account = config.get("account")
    project = config.get("project")
    if account:
        _gcloud("set", "account", account)
    if project:
        _gcloud("set", "project", project)
