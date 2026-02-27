from pathlib import Path


# Paths
BASE_PATH = Path(__file__).resolve().parent
BASE_FOLDER = str(BASE_PATH) + '/'

DATA_FOLDER = f'{BASE_FOLDER}data/'
Path(DATA_FOLDER).mkdir(exist_ok=True)


# DBs

# sqlite API DB parameters
API_DB = f'{DATA_FOLDER}job_requests.db'
REPLACE_API_DB = False
JSON_SERVICES = f'{DATA_FOLDER}services.json'

# sqlite scheduler DB parameters
REPLACE_SCHEDULER_DB = False
SCHEDULER_DB = f'{DATA_FOLDER}scheduler.db'


# Scheduler parameters
SCHEDULER_INTERVAL = 8
DEF_BATCH = 100
UNKNOWN_STATUS = 'unknown'
RUN_ONCE = False
GLOBAL_CONCURRENCY = 100
#
MIN_BACKOFF = 2 # seconds
MAX_BACKOFF = 60 # seconds


# Service parameters
DEFAULT_STATUS_FIELD = 'status'
DEFAULT_SERVICE_MAX_CONCURRENCY = 10
DEFAULT_SERVICE_TIMEOUT = 2



