from datetime import datetime, timezone
from pathlib import Path
import sqlite3


def utcnow():
    return datetime.now(timezone.utc)

def timestamp_for_filename(datetime_):
    return datetime_.strftime('%Y-%m-%d_T%H-%M-%S.%fZ')

def timestamp_for_db(datetime_):
    return datetime_.strftime('%Y-%m-%d_T%H:%M:%S.%fZ')


def backup_file(path):

    file = Path(path)
    if not file.exists():
        return

    timestamp = timestamp_for_filename(utcnow())
    backup = file.with_name(f"{file.name}_{timestamp}.bak")

    file.rename(backup)
