from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def utcnow_filename():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d_T%H-%M-%S.%fZ')
