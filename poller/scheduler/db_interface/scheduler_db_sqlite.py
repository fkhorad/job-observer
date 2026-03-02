import sqlite3

from poller.config import SCHEDULER_DB, REPLACE_DBS
from poller.config import UNKNOWN_STATUS
from poller.general_helpers import utcnow, backup_file, timestamp_for_db

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

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
            observed_state TEXT NOT NULL,
            unchanged_count INTEGER NOT NULL DEFAULT 0,
            next_poll_at TEXT NOT NULL,
            is_terminal INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            terminal_at DATETIME,
            UNIQUE(job_id, service)
        )
        """)

##########
# QUERIES
##########

# LAST SEQ (=last job imported from api_db)
def get_last_seq(conn):
    last_seq = conn.execute(
        "SELECT last_seq FROM controller_cursor WHERE id=1"
    ).fetchone()[0]
    return {'last_seq': last_seq}


# JOBS
def insert_jobs(conn, job_rows):
    try:
        conn.execute("BEGIN IMMEDIATE;")
        #
        for _, job_id, service in job_rows:
            _insert_job(conn, job_id, service)
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
def _insert_job(conn, job_id, service):
    conn.execute("""
        INSERT OR IGNORE INTO job_state(job_id, service, observed_state, next_poll_at, updated_at)
        VALUES(?, ?, ?, datetime('now'), datetime('now'))
    """, (job_id, service, UNKNOWN_STATUS))
#
def get_jobs_by_id(conn, job_id):
    conn.row_factory = dict_factory
    return conn.execute("""
        SELECT job_id, service, observed_state, unchanged_count, is_terminal
        FROM job_state
        WHERE job_id = ?
    """, (job_id, )).fetchall()
#
def get_due_jobs(conn):
    return conn.execute("""
        SELECT job_id, service, observed_state, unchanged_count
        FROM job_state
        WHERE is_terminal = 0
        AND next_poll_at <= ?
    """, (timestamp_for_db(utcnow()),)).fetchall()
#
def update_jobs(conn, dressed_results):

    try:
        conn.execute("BEGIN IMMEDIATE;")
        #
        for dressed_result in dressed_results:
            result = dressed_result['result']
            job_id = result['job_id']
            service = result['service']
            new_state = result['new_state']
            unchanged_count = result.get('unchanged_count', 0)
            next_poll = result['next_poll']
            is_terminal = result['is_terminal']
            #
            _update_job(conn, job_id, service, new_state, unchanged_count, next_poll, is_terminal)
        #
        conn.execute("COMMIT;")
    except Exception:
        conn.execute("ROLLBACK;")
        raise # Reraises the SAME exception with the same traceback
#
def _update_job(conn, job_id, service, new_state, unchanged_count, next_poll, is_terminal):

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
        new_state,
        unchanged_count,
        timestamp_for_db(next_poll),
        int(is_terminal),
        now,
        now,
        job_id,
        service
    ))




