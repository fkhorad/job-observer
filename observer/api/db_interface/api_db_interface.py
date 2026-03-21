# Job Observer
# Copyright (c) 2025 Name Surname
# Licensed under the MIT License. See LICENSE file in the project root.

from observer.api.db_interface.api_db_sqlite import init_api_sqlite_db, init_scheduler_sqlite_db, insert_job, get_new_jobs
from observer.api.db_interface.service_jsondb import get_services, get_services_filtered, init_db as init_services_db, add_services
from observer.config import DEF_BATCH


# Change here (+ config) only if not sqlite
# NOTE: this initializes ALL DBs, not just the API one
def init_db():
    init_services_db()
    init_scheduler_sqlite_db() # Initialized here in the api package, NOT in the scheduler package!
    init_api_sqlite_db()

def get_db(**kwargs):
    return SQLITE_DB(**kwargs)


################################
# sqlite (+ temp JSON interface)
################################
import sqlite3
from pathlib import Path
from observer.config import API_DB

class SQLITE_DB:

    def __init__(self, *, read_only: bool = False, no_connection: bool = False):
        self.read_only = read_only
        self.no_connection = no_connection
        self.conn = None

    def __enter__(self):
        
        if self.no_connection:
            return self

        db_path = Path(API_DB).resolve()
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

    def insert_job(self, job_id, service, callback_url):
        insert_job(self.conn, job_id, service, callback_url)

    def get_new_jobs(self, new_jobs_parameters, batch=DEF_BATCH):
        last_seq = new_jobs_parameters['last_seq']
        new_jobs = get_new_jobs(self.conn, last_seq, batch)
        limit_hit = bool(new_jobs and len(new_jobs)>=batch)
        return new_jobs, limit_hit


    def get_services(self):
        return get_services()
    
    def add_services(self, data, overwrite):
        return add_services(data, overwrite)

    def get_services_filtered(self):
        return get_services_filtered()