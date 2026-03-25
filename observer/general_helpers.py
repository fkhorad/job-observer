from datetime import datetime, timezone
from pathlib import Path
import logging
import os


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

    # Try to read from env
    logging_level_keyword = os.getenv('LOGGING_LEVEL', 'INFO').upper().strip()
    #
    if logging_level_keyword=='DEBUG':
        logging_level = logging.DEBUG
    elif logging_level_keyword=='WARNING':
        logging_level = logging.WARNING
    elif logging_level_keyword=='ERROR':
        logging_level = logging.ERROR
    elif logging_level_keyword=='CRITICAL':
        logging_level = logging.CRITICAL


    # Setup the root logger
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    )
