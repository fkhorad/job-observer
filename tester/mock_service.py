from fastapi import FastAPI
import random
import time


app = FastAPI()

STATUSES = {}

##
PENDING = 'pending'
RUNNING = 'running'
DONE = 'done'
TIMED_OUT = 'timed out'
TIMEOUT = 50

@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = STATUSES.get(job_id)

    timestamp = time.perf_counter()
    if job is None:
        status = PENDING
        STATUSES[job_id] = {'status': status, 'timestamp': timestamp}
    else:
        status = job['status']
        elapsed = time.perf_counter() - job['timestamp']
        if status != DONE and elapsed>TIMEOUT:
            status = TIMED_OUT

    if status==PENDING:
        status = random.choice([PENDING, RUNNING, DONE])
    elif status==RUNNING:
        status = random.choice([RUNNING, DONE])

    STATUSES[job_id]['status'] = status

    return {"status": status}

