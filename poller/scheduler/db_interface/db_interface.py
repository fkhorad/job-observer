import sqlite3

from poller.scheduler.db_interface.scheduler_db_sqlite import init_sqlite_db, get_last_seq, insert_job, update_last_seq, update_job, get_jobs_by_id


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
    def __init__(self):
        self.conn = sqlite3.connect(SCHEDULER_DB)

    # TODO: consider refactoring
    def clean(self):
        self.conn.commit()
        self.conn.close()

    def get_last_seq(self):
        return get_last_seq(self.conn)
    
    def insert_job(self, job_id, service):
        insert_job(self.conn, job_id, service)
    
    def update_last_seq(self, last_seq):
        update_last_seq(self.conn, last_seq)

    def get_due_jobs(self):
        return self.get_due_jobs(self.conn)
    
    def update_job(self, job_id, new_state, unchanged_count, next_poll, is_terminal):
        update_job(self.conn, job_id, new_state, unchanged_count, next_poll, is_terminal)

    def get_jobs_by_id(self, job_id):
        return get_jobs_by_id(self.conn, job_id)