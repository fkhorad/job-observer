import sqlite3

from poller.config import API_DB as DB, REPLACE_DBS
from poller.general_helpers import backup_file


def init_sqlite_db():

    if REPLACE_DBS:
        backup_file(DB)


    with sqlite3.connect(DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS job_requests (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            service TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_job ON job_requests(job_id, service)")


def get_new_jobs(last_seq, batch):
    with sqlite3.connect(DB) as conn:
        res = conn.execute("""
            SELECT seq, job_id, service
            FROM job_requests
            WHERE seq > ?
            ORDER BY seq
            LIMIT ?
        """, (last_seq, batch)).fetchall()
        return res


# This is the only write operation for now; check connection configuration
def insert_job(job_id, service):
    with sqlite3.connect(DB, timeout=5, isolation_level=None) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO job_requests(job_id, service) VALUES (?,?)",
            (job_id, service),
        )
