from datetime import datetime, timezone
from pathlib import Path
import logging

from observer.config import LOGGING_LEVEL, APP_NAMESPACE


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

    # Logging level
    
    # Default
    logging_level = logging.INFO

    logging_level_keyword = LOGGING_LEVEL.upper().strip() if LOGGING_LEVEL else ''

    # Try to read from env
    #
    if logging_level_keyword=='DEBUG':
        logging_level = logging.DEBUG
    elif logging_level_keyword=='WARNING':
        logging_level = logging.WARNING
    elif logging_level_keyword=='ERROR':
        logging_level = logging.ERROR
    elif logging_level_keyword=='CRITICAL':
        logging_level = logging.CRITICAL

    logging_format="%(asctime)s [%(name)s] %(levelname)s | %(message)s"

    # Set logger for app
    logger = logging.getLogger(APP_NAMESPACE)

    logger.setLevel(logging_level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(logging_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False  # prevents duplication via root
