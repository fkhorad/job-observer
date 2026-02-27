import sqlite3

from poller.scheduler.db_interface.scheduler_db_sqlite import init_sqlite_db, get_last_seq, insert_job, update_last_seq, update_job, get_jobs_by_id, get_due_jobs


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
        # TODO: cross-check this connection settings (should be able to handle concurrency)
        conn = sqlite3.connect(SCHEDULER_DB, timeout=5, isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        self.conn = conn
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.commit()
        self.conn.close()

    def get_new_jobs_parameters(self):
        return get_last_seq(self.conn)
    
    def insert_job(self, job_id, service):
        insert_job(self.conn, job_id, service)
    
    def update_new_jobs_parameters(self, job_rows):
        last_seq = max([r[0] for r in job_rows])
        update_last_seq(self.conn, last_seq)

    def get_due_jobs(self):
        return get_due_jobs(self.conn)
    
    def update_job(self, result):
        job_id = result['job_id']
        service = result['service']
        new_state = result['new_state']
        unchanged_count = result.get('unchanged_count', 0)
        next_poll = result['next_poll']
        is_terminal = result['is_terminal']

        update_job(self.conn, job_id, service, new_state, unchanged_count, next_poll, is_terminal)

    def get_jobs_by_id(self, job_id):
        return get_jobs_by_id(self.conn, job_id)