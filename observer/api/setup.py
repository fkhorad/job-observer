import sys
from fastapi import Header, HTTPException, status
import os
import logging

from observer.api.db_interface.api_db_interface import init_db
from observer.config import DATA_FOLDER, SETUP_KEY


logger = logging.getLogger(__name__)

def bootstrap():
    try:
        create_data_folder()
        init_db()
    except Exception as e:
        logger.critical(f'Setup failure: {type(e).__name__}: {e}')
        sys.exit(1) # Hard exit; can prevent hangs on systemd


def create_data_folder():
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    # Write test
    test_file = DATA_FOLDER / ".write_test"
    test_file.touch()
    test_file.unlink() # Delete the test file
    

# --- Auth dependency ---
def get_api_key(setup_key: str | None = Header(default=None)):
    if not SETUP_KEY:
        logger.error("Admin attempted setup, but SETUP_KEY is not configured in .env")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    if not setup_key or setup_key != SETUP_KEY:
        logger.warning("Invalid setup key provided.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return setup_key
