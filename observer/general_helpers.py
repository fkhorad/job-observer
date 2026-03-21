from datetime import datetime, timezone
from pathlib import Path
import logging
import sys

from observer.config import LOGGER_NAME, LOGGING_LEVEL


def utcnow():
    return datetime.now(timezone.utc)

def timestamp_for_filename(datetime_):
    return datetime_.strftime('%Y-%m-%d_T%H-%M-%S.%fZ')

def timestamp_for_db(datetime_):
    if datetime_ is None:
        return None
    return datetime_.strftime('%Y-%m-%d_T%H:%M:%S.%fZ')


def backup_file(path: Path|str):

    file = Path(path).resolve()
    if not file.exists():
        return

    timestamp = timestamp_for_filename(utcnow())
    backup = file.with_name(f"{file.name}_{timestamp}.bak")

    file.rename(backup)


def config_logging():

    # Create/Get the logger
    logger = logging.getLogger(LOGGER_NAME)

    # Set level
    logger.setLevel(LOGGING_LEVEL)

    # Set handlers if not already set
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Stop propagation to keep other libs (es. Gunicorn) root loggers from doubling the output
    logger.propagate = False

    return logger
