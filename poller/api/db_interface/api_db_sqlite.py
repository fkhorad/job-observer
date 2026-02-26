import sqlite3

from poller.config import API_DB as DB


def init_sqlite_db():
    with sqlite3.connect(DB) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS job_requests (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            service TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_job ON job_requests(job_id)")


def insert_job(job_id, service):
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO job_requests(job_id, service) VALUES (?,?)",
            (job_id, service),
        )
