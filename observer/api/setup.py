from pathlib import Path
import sys

from observer.api.db_interface.api_db_interface import init_db
from observer.config import DATA_FOLDER, JSON_SERVICES_FOLDER, config_logging


def bootstrap():
    logger = config_logging()
    try:
        create_foldering()
        init_db()
    except Exception as e:
        logger.critical(f'Setup failure: {type(e).__name__}: {e}')
        sys.exit(1) # Hard exit; can prevent hangs on systemd


def create_foldering():
    datapath = Path(DATA_FOLDER)
    datapath.mkdir(parents=True, exist_ok=True)
    Path(JSON_SERVICES_FOLDER).mkdir(parents=True, exist_ok=True)

    # Write test
    test_file = datapath / ".write_test"
    test_file.touch()
    test_file.unlink() # Delete the test file
    
