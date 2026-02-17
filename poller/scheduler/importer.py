import sqlite3

from poller.config import SCHEDULER_DB as CTRL_DB, API_DB, DEF_BATCH, UNKNOWN


def import_jobs(api_con, sched_con, batch=DEF_BATCH):
    last_seq = sched_con.execute(
        "SELECT last_seq FROM controller_cursor WHERE id=1"
    ).fetchone()[0]

    with sqlite3.connect(API_DB) as api:
        rows = api_con.execute("""
            SELECT seq, job_id, service
            FROM job_requests
            WHERE seq > ?
            ORDER BY seq
            LIMIT ?
        """, (last_seq, batch)).fetchall()

    for seq, job_id, service in rows:
        sched_con.execute("""
            INSERT INTO job_state(job_id, service, observed_state, next_poll_at, updated_at)
            VALUES(?, ?, ?, datetime('now'), datetime('now'))
            ON CONFLICT(job_id) DO UPDATE SET
                service=excluded.service
        """, (job_id, service, UNKNOWN))
        last_seq = seq

    sched_con.execute(
        "UPDATE controller_cursor SET last_seq=? WHERE id=1",
        (last_seq,),
    )
