from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR/"data"
DATA_DIR.mkdir(exist_ok=True)

API_DB = DATA_DIR/"job_requests.db"
SCHEDULER_DB = DATA_DIR/"scheduler.db"
#
DEF_BATCH = 100
UNKNOWN = 'unknown'
#
CLIENT_TIMEOUT = 2
SCHEDULER_INTERVAL = 5

