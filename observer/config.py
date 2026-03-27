from pathlib import Path
import os


# Data folder absolute path (Path obj)
DATA_FOLDER = Path( os.getenv('OBSERVER_DATA_DIR', Path(__file__).resolve().parent.parent / 'data') ).resolve()

# DBs
REPLACE_DBS = False

# sqlite API DB parameters
API_DB = DATA_FOLDER / 'job_requests.db'

LOGGING_LEVEL = os.getenv('LOGGING_LEVEL')


# services DB parameters
JSON_SERVICES_FOLDER = DATA_FOLDER / 'services'
JSON_SERVICES_FILE = JSON_SERVICES_FOLDER / 'services.json'
SETUP_KEY = os.getenv('SETUP_KEY') # Required to set services through POST API

# sqlite scheduler DB parameters
SCHEDULER_DB = DATA_FOLDER / 'scheduler.db'


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




