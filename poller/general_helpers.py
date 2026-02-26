from datetime import datetime, timezone
from pathlib import Path


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def utcnow_filename():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d_T%H-%M-%S.%fZ')


def backup_file(path):

    file = Path(path)
    if not file.exists():
        return

    timestamp = utcnow_filename()
    backup = file.with_name(f"{file.name}_{timestamp}.bak")

    file.rename(backup)
