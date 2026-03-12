# Job Observer
# Copyright (c) 2025 Name Surname
# Licensed under the MIT License. See LICENSE file in the project root.

import sqlite3
from pathlib import Path

from observer.config import API_DB as DB, REPLACE_DBS, SCHEDULER_DB as SCHED_DB
from observer.general_helpers import utcnow, backup_file, timestamp_for_db


##################
# DB (RE)CREATION
##################

def init_sqlite_db():

    if REPLACE_DBS:
        backup_file(DB)

    with sqlite3.connect(DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS job_requests (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            service TEXT NOT NULL,
            callback_url TEXT,
            created_at DATETIME
        )
        """)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_job ON job_requests(job_id, service)")

    sequence_check()

def sequence_check():

    # Check last_seq value in SCHED_DB; if SCHED_DB does not exist yet, if last_seq there is not initialized, or if its value is 0, just silently return -- all these scenarios are possible and consistent
    try:
        db_path = Path(SCHED_DB).resolve() # Handles OS-dependent (Windows...) vagaries in path handling
        with sqlite3.connect(f'{db_path.as_uri()}?mode=ro', uri=True) as sched_conn: # open in read-only ONLY IF SCHEDULER DB ALREADY EXISTS
            last_seq_check = sched_conn.execute("SELECT last_seq FROM controller_cursor WHERE id=1").fetchone()
            if not last_seq_check:
                return
            sched_last_seq = last_seq_check[0]
        if sched_last_seq==0:
            return
    except:
        return

    # If we have a nonzero value of last_seq in SCHED_DB, the actual consistency check starts.
    # Note that this SHOULD NOT BE NECESSARY IN GENERAL, but inconsistency can happen in testing condition and could conceivably surface in some restart situations in prod; this consistency constraint should never be harmful in any case, so it makes sense to keep it.
    with sqlite3.connect(DB) as conn:

        # Check local status
        row = conn.execute("SELECT seq FROM sqlite_sequence WHERE name = 'job_requests'").fetchone()
        
        if row:
            seq_val = row[0]

            # If seq exists but scheduler value is higher, update seq to scheduler value; this should ensure that next inserted job is actually picked up
            if sched_last_seq > seq_val:
                conn.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'job_requests'", (sched_last_seq, ))
        else:
            # If seq doesn't exist yet, initialize it to scheduler value 
            conn.execute("INSERT OR REPLACE INTO sqlite_sequence (name, seq) VALUES (?, ?)", ('job_requests', sched_last_seq))


##########
# QUERIES
##########

def get_new_jobs(conn, last_seq, batch):
    res = conn.execute("""
        SELECT seq, job_id, service, callback_url
        FROM job_requests
        WHERE seq > ?
        ORDER BY seq
        LIMIT ?
    """, (last_seq, batch)).fetchall()
    return res

# This is the only write operation for now
def insert_job(conn, job_id, service, callback_url):
    now = timestamp_for_db(utcnow())
    conn.execute("INSERT OR IGNORE INTO job_requests(job_id, service, callback_url, created_at) VALUES (?, ?, ?, ?)", (job_id, service, callback_url, now))


