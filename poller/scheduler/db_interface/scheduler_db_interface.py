import sqlite3

from poller.scheduler.db_interface.scheduler_db_sqlite import init_sqlite_db, get_last_seq, insert_jobs, update_jobs, get_jobs_by_id, get_due_jobs, fetch_pending_callbacks
from poller.config import DEF_BATCH


# Change here (+ config) only if not sqlite
def init_db():
    init_sqlite_db()

def get_db():
    return SQLITE_DB()


##################
# sqlite interface
##################
from poller.config import SCHEDULER_DB

class SQLITE_DB:

    def __enter__(self):
        conn = sqlite3.connect(SCHEDULER_DB, timeout=5, isolation_level=None) # CARE: isolation_level=None implies true autocommit --> manual handling of transactions when they involve multiple statement
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        self.conn = conn
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.close()

    def get_new_jobs_parameters(self):
        return get_last_seq(self.conn)
    
    def insert_jobs(self, job_rows):
        insert_jobs(self.conn, job_rows)

    def get_due_jobs(self, batch=DEF_BATCH):
        due_jobs = get_due_jobs(self.conn, batch)
        limit_hit = bool(due_jobs and len(due_jobs)==batch)
        return due_jobs, limit_hit

    def fetch_pending_callbacks(self, batch=DEF_BATCH):
        pending_callbacks = fetch_pending_callbacks(self.conn, batch)
        limit_hit = bool(pending_callbacks and len(pending_callbacks)==batch)
        return pending_callbacks, limit_hit

    def update_jobs(self, dressed_results):
        update_jobs(self.conn, dressed_results)

    def get_jobs_by_id(self, job_id):
        return get_jobs_by_id(self.conn, job_id)