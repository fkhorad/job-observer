import sqlite3

from poller.api.db_interface.api_db_sqlite import init_sqlite_db, insert_job, get_new_jobs
from poller.api.db_interface.service_db_fake import get_services
from poller.config import DEF_BATCH


# Change here (+ config) only if not sqlite
def init_db():
    init_sqlite_db()

def get_db():
    return SQLITE_DB()


################################
# sqlite (+ temp JSON interface)
################################
from poller.config import API_DB

class SQLITE_DB:
    def __enter__(self):
        conn = sqlite3.connect(API_DB, timeout=5, isolation_level=None) # CARE: isolation_level=None implies true autocommit --> manual handling of transactions when they involve multiple statement
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        self.conn = conn
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.close()

    def insert_job(self, job_id, service):
        insert_job(self.conn, job_id, service)

    def get_new_jobs(self, new_jobs_parameters, batch=DEF_BATCH):
        last_seq = new_jobs_parameters['last_seq']
        return get_new_jobs(last_seq, batch)


    # TODO: refactor, eventually (?)
    def get_services(self):
        return get_services()