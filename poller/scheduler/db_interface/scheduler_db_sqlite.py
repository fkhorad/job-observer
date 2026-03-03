import sqlite3

from poller.config import SCHEDULER_DB, REPLACE_DBS, UNKNOWN_STATUS
from poller.general_helpers import utcnow, backup_file, timestamp_for_db
from poller.scheduler.dtos.job import Job
from poller.scheduler.db_interface.services_interface import DUMMY_SERVICE
from poller.scheduler.callback import Callback, PENDING


##################
# DB (RE)CREATION
##################

def init_sqlite_db():

    if REPLACE_DBS:
        backup_file(SCHEDULER_DB)

    # Create tables (AND db file if necessary)
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
            callback_url TEXT,
            observed_state TEXT NOT NULL,
            unchanged_count INTEGER NOT NULL DEFAULT 0,
            next_poll_at TEXT NOT NULL,
            is_terminal INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            terminal_at DATETIME,
            UNIQUE(job_id, service)
        )
        """)

        # Callback outbox
        conn.execute(f"""
        CREATE TABLE IF NOT EXISTS callback_outbox (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id TEXT NOT NULL,
            callback_url TEXT NOT NULL,
            job_terminal_state TEXT NOT NULL,

            callback_state TEXT NOT NULL DEFAULT '{PENDING}',
            retry_count INTEGER NOT NULL DEFAULT 0,

            created_at DATETIME NOT NULL,
            next_attempt_at DATETIME NOT NULL,

            last_error TEXT,
            delivered_at DATETIME,
            service TEXT DEFAULT '{DUMMY_SERVICE}'
        );
        """)

        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_callback_pending
            ON callback_outbox (callback_state, next_attempt_at);
        """)

##########
# QUERIES
##########

# Helper
def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def job_factory(cursor, row):
    return Job._make(row)

def callback_factory(cursor, row):
    return Callback(**{col[0]: row[idx] for idx, col in enumerate(cursor.description)})


# LAST SEQ (=last job imported from api_db)
def get_last_seq(conn):
    last_seq = conn.execute(
        "SELECT last_seq FROM controller_cursor WHERE id=1"
    ).fetchone()[0]
    return {'last_seq': last_seq}


# JOBS

## GET info
def get_jobs_by_id(conn, job_id, service):
    conn.row_factory = dict_factory
    return conn.execute("""
        SELECT job_id, service, observed_state, unchanged_count, is_terminal
        FROM job_state
        WHERE job_id = ? AND service = ?
    """, (job_id, service)).fetchall()
#
def get_due_jobs(conn, batch):
    conn.row_factory = job_factory
    return conn.execute("""
        SELECT job_id, service, observed_state, unchanged_count, next_poll_at, is_terminal, callback_url
        FROM job_state
        WHERE is_terminal = 0
        AND next_poll_at <= ?
        LIMIT ?
    """, (timestamp_for_db(utcnow()), batch)).fetchall()
#
def fetch_pending_callbacks(conn, batch):
    conn.row_factory = callback_factory
    return conn.execute(f"""
        SELECT id, job_id, callback_url, job_terminal_state, retry_count, next_attempt_at, created_at, callback_state, service, last_error, delivered_at
        FROM callback_outbox
        WHERE callback_state = '{PENDING}'
        AND next_attempt_at <= CURRENT_TIMESTAMP
        ORDER BY created_at
        LIMIT ?
    """, (batch,)).fetchall()


## Insert/Update
def insert_jobs(conn, job_rows):
    try:
        conn.execute("BEGIN IMMEDIATE;") # Manual handling as I want multiple executes in single transaction in autocommit mode
        #
        for _, job_id, service, callback_url in job_rows:
            _insert_job(conn, job_id, service, callback_url)
        #
        last_seq = max([r[0] for r in job_rows])
        _update_last_seq(conn, last_seq)
        conn.execute("COMMIT;")
    except Exception:
        conn.execute("ROLLBACK;")
        raise # Reraises the SAME exception with the same traceback
#
def _update_last_seq(conn, last_seq):
    conn.execute("UPDATE controller_cursor SET last_seq=? WHERE id=1", (last_seq,))
#
def _insert_job(conn, job_id, service, callback_url):
    now = timestamp_for_db(utcnow())
    conn.execute("""
        INSERT OR IGNORE INTO job_state(job_id, service, callback_url, observed_state, next_poll_at, updated_at)
        VALUES(?, ?, ?, ?, ?, ?)
    """, (job_id, service, callback_url, UNKNOWN_STATUS, now, now))
#
def update_jobs(conn, dressed_results):
    try:
        conn.execute("BEGIN IMMEDIATE;") # Manual handling as I want multiple executes in single transaction in autocommit mode
        #
        for dressed_result in dressed_results:
            job = dressed_result.get('result')
            if job is None:
                continue
            #
            _update_job(conn, job)
            if job.callback_url is not None and job.is_terminal:
                _insert_callback(conn, job.job_id, job.callback_url, job.new_state)
        #
        conn.execute("COMMIT;")
    except Exception:
        conn.execute("ROLLBACK;")
        raise # Reraises the SAME exception with the same traceback
#
def _update_job(conn, job):
    now = timestamp_for_db(utcnow())
    conn.execute("""
        UPDATE job_state
        SET observed_state=?,
            unchanged_count=?,
            next_poll_at=?,
            is_terminal=?,
            terminal_at =
                CASE
                    WHEN is_terminal = 1 AND terminal_at IS NULL THEN ?
                    ELSE terminal_at
                END,
            updated_at=?
        WHERE job_id=? AND service=?
    """, (
        job.state,
        job.unchanged_count,
        timestamp_for_db(job.next_poll_at),
        int(job.is_terminal),
        now,
        now,
        job.job_id,
        job.service
    ))

def _insert_callback(conn, job_id, callback_url, terminal_state):
    now = timestamp_for_db(utcnow())
    conn.execute("""
        INSERT INTO callback_outbox (
            job_id,
            callback_url,
            terminal_state,
            max_retries,
            created_at,
            next_attempt_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        callback_url,
        terminal_state,
        now,
        now
    ))
#
def update_callbacks(conn, dressed_results):
    try:
        conn.execute("BEGIN IMMEDIATE;") # Manual handling as I want multiple executes in single transaction in autocommit mode
        #
        for dressed_result in dressed_results:
            callback = dressed_result.get('result')
            if callback is None:
                continue
            #
            _update_callback(conn, callback)
        #
        conn.execute("COMMIT;")
    except Exception:
        conn.execute("ROLLBACK;")
        raise # Reraises the SAME exception with the same traceback
#
def _update_callback(conn, callback):
    conn.execute("""
        UPDATE job_state
        SET callback_state = ?, retry_count = ?, next_attempt_at = ?, last_error = ?, delivered_at = ?
        """, (callback.callback_state, callback.retry_count, timestamp_for_db(callback.next_attempt_at)), callback.last_error, timestamp_for_db(callback.delivered_at))



