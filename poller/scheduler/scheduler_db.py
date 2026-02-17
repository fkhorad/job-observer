import sqlite3
from datetime import datetime, timezone

from poller.config import SCHEDULER_DB


def init_scheduler_db():
    with sqlite3.connect(SCHEDULER_DB) as con:
        
        # Special 'single-row' table
        con.execute("""
        CREATE TABLE IF NOT EXISTS controller_cursor (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            last_seq INTEGER NOT NULL
        )
        """)
        con.execute("""
        INSERT OR IGNORE INTO controller_cursor(id, last_seq) VALUES (1,0)
        """)

        # Job table
        con.execute("""
        CREATE TABLE IF NOT EXISTS job_state (
            job_id TEXT PRIMARY KEY,
            service TEXT NOT NULL,
            observed_state TEXT NOT NULL,
            unchanged_count INTEGER NOT NULL DEFAULT 0,
            next_poll_at TEXT NOT NULL,
            is_terminal INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
        """)


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def get_due_jobs(con):
    return con.execute("""
        SELECT job_id, service, observed_state, unchanged_count
        FROM job_state
        WHERE is_terminal = 0
        AND next_poll_at <= ?
    """, (utcnow(),)).fetchall()


def upsert_job(con, job_id, service):
    now = utcnow()
    con.execute("""
        INSERT OR IGNORE INTO job_state
        (job_id, service, observed_state, next_poll_at, updated_at)
        VALUES (?, ?, 'pending', ?, ?)
    """, (job_id, service, now, now))
