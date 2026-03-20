from pathlib import Path
import logging
import sys


# Paths
BASE_PATH = Path(__file__).resolve().parent.parent
BASE_FOLDER = str(BASE_PATH) + '/'

DATA_FOLDER = f'{BASE_FOLDER}data/'


# DBs
REPLACE_DBS = False

# sqlite API DB parameters
API_DB = f'{DATA_FOLDER}job_requests.db'

# services DB parameters
JSON_SERVICES_FOLDER = f'{DATA_FOLDER}services/'
JSON_SERVICES_FILE = f'{JSON_SERVICES_FOLDER}services.json'

# sqlite scheduler DB parameters
SCHEDULER_DB = f'{DATA_FOLDER}scheduler.db'


# Scheduler parameters
SCHEDULER_IDLE_SLEEP = 5
SCHEDULER_BUSY_SLEEP = 0.5
DEF_BATCH = 100
UNKNOWN_STATUS = 'unknown'
RUN_ONCE = False
GLOBAL_CONCURRENCY = 100
CALLBACK_RETRIES = 15
#
MIN_BACKOFF = 2 # seconds
MAX_BACKOFF = 60 # seconds


# Service parameters
DEFAULT_STATUS_FIELD = 'status'
DEFAULT_SERVICE_MAX_CONCURRENCY = 10
DEFAULT_SERVICE_TIMEOUT = 2
GLOBAL_PSEUDOSERVICE = '#GLOBAL_PSEUDOSERVICE#'
DUMMY_SERVICE = '#DUMMY#'


# Logging
LOGGING_LEVEL = logging.DEBUG
LOGGER_NAME = 'observer'
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




