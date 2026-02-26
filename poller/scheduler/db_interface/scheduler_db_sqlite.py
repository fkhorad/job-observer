import sqlite3

from poller.config import SCHEDULER_DB, REPLACE_SCHEDULER_DB
from poller.config import UNKNOWN_STATUS
from poller.general_helpers import utcnow, backup_file


def init_sqlite_db():

    if REPLACE_SCHEDULER_DB:
        backup_file(SCHEDULER_DB)

    # Create tables (AND db file)
    with sqlite3.connect(SCHEDULER_DB) as conn:
        
        # Special 'single-row' table, containing last checked job id
        conn.execute("""
        CREATE TABLE IF NOT EXISTS controller_cursor (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            last_seq INTEGER NOT NULL
        )
        """)
        conn.execute("""
        INSERT OR IGNORE INTO controller_cursor(id, last_seq) VALUES (1,0)
        """)

        # Job table
        conn.execute("""
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

# Queries

# LAST SEQ (=last job imported from api_db)
def get_last_seq(conn):
    last_seq = conn.execute(
        "SELECT last_seq FROM controller_cursor WHERE id=1"
    ).fetchone()[0]
    return {'last_seq': last_seq}
#
def update_last_seq(conn, last_seq):
    conn.execute(
        "UPDATE controller_cursor SET last_seq=? WHERE id=1",
        (last_seq,),
    )


# JOBS

def insert_job(conn, job_id, service):
    conn.execute("""
        INSERT INTO job_state(job_id, service, observed_state, next_poll_at, updated_at)
        VALUES(?, ?, ?, datetime('now'), datetime('now'))
        ON CONFLICT(job_id) DO UPDATE SET
            service=excluded.service
    """, (job_id, service, UNKNOWN_STATUS))

def get_jobs_by_id(conn, job_id):
    return conn.execute("""
        SELECT job_id, service, observed_state, unchanged_count
        FROM job_state
        WHERE job_id = ?
    """, (job_id, )).fetchall()


def get_due_jobs(conn):
    return conn.execute("""
        SELECT job_id, service, observed_state, unchanged_count
        FROM job_state
        WHERE is_terminal = 0
        AND next_poll_at <= ?
    """, (utcnow(),)).fetchall()

def update_job(conn, job_id, new_state, unchanged_count, next_poll, is_terminal):
    conn.execute("""
        UPDATE job_state
        SET observed_state=?,
            unchanged_count=?,
            next_poll_at=?,
            is_terminal=?,
            updated_at=?
        WHERE job_id=?
    """, (
        new_state,
        unchanged_count,
        next_poll.isoformat(),
        int(is_terminal),
        utcnow(),
        job_id
    ))




