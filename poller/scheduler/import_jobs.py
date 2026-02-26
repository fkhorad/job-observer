import sqlite3

from poller.config import API_DB, DEF_BATCH


def import_jobs(db, batch=DEF_BATCH):

    last_seq = db.get_last_seq()

    with sqlite3.connect(API_DB) as api_conn:
        rows = api_conn.execute("""
            SELECT seq, job_id, service
            FROM job_requests
            WHERE seq > ?
            ORDER BY seq
            LIMIT ?
        """, (last_seq, batch)).fetchall()

    for seq, job_id, service in rows:
        db.insert_job(job_id, service)
        last_seq = seq

    db.update_last_seq(last_seq)