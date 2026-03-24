# Job Observer
# Copyright (c) 2025 Name Surname
# Licensed under the MIT License. See LICENSE file in the project root.

from observer.scheduler.db_interface.scheduler_db_sqlite import get_last_seq, insert_jobs, update_jobs, get_jobs_by_id, get_due_jobs, fetch_pending_callbacks, update_callbacks, check_heartbeat, upsert_heartbeat
from observer.config import DEF_BATCH


# Change here (+ config) only if not sqlite
def check_db():
    try:
        with get_db() as db_check: # Meant to CRUSH if DB not initialized (via API)
            pass
    except sqlite3.OperationalError:
        raise Exception('DB not initialized')

def get_db(**kwargs):
    return SQLITE_DB(**kwargs)


##################
# sqlite interface
##################
import sqlite3
from pathlib import Path
from observer.config import SCHEDULER_DB

class SQLITE_DB:

    def __init__(self, *, read_only: bool = False):
        self.read_only = read_only
        self.conn = None

    def __enter__(self):
        
        db_path = Path(SCHEDULER_DB).resolve()
        # CARE: isolation_level=None implies true autocommit --> manual handling of transactions when they involve multiple statement
        if self.read_only:
            conn = sqlite3.connect(f'{db_path.as_uri()}?mode=ro', uri=True, timeout=5, isolation_level=None) 
        else:
            conn = sqlite3.connect(f'{db_path.as_uri()}?mode=rw', uri=True, timeout=5, isolation_level=None) 
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        #
        conn.execute("PRAGMA busy_timeout=5000;")
        self.conn = conn
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.conn is not None:
            self.conn.close()

    def check_heartbeat(self):
        return check_heartbeat(self)

    def upsert_heartbeat(self):
        return upsert_heartbeat(self)

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

    def update_callbacks(self, dressed_results):
        update_callbacks(self.conn, dressed_results)

    def get_jobs_by_id(self, job_id, service):
        return get_jobs_by_id(self.conn, job_id, service)