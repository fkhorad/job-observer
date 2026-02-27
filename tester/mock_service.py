from fastapi import FastAPI, Request, HTTPException
import random
import time
import secrets
import string
from contextlib import asynccontextmanager
import asyncio


## Constants
PENDING = 'pending'
RUNNING = 'running'
DONE = 'done'
TIMED_OUT = 'timed out'
TIMEOUT = 50



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.counter = 0
    app.state.lock = asyncio.Lock()
    app.state.cache = {}

    yield

    # shutdown (optional cleanup)
    app.state.cache.clear()

app = FastAPI(lifespan=lifespan)


@app.post("/job")
async def create_job(req: Request):
    async with req.app.state.lock:
        id = get_random_string(6)
        job_id = f'{id}-{req.app.state.counter}'
        timestamp = time.perf_counter()
        req.app.state.cache[job_id] = {'status': PENDING, 'timestamp': timestamp}
        req.app.state.counter += 1
        return {'job_id': job_id}


# Should be GET, but...
@app.post("/status/{job_id}")
async def get_status(job_id: str, req: Request):
    async with req.app.state.lock:

        job = req.app.state.cache.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        elapsed = time.perf_counter() - job['timestamp']

        if status != DONE and elapsed>TIMEOUT:
            status = TIMED_OUT
        elif status==PENDING:
            status = random.choice([PENDING, RUNNING, DONE])
        elif status==RUNNING:
            status = random.choice([RUNNING, DONE])

        req.app.state.cache[job_id]['status'] = status

        return {"status": status}


# Helper
ALPHABET = string.ascii_uppercase + string.digits

def get_random_string(length: int, *, alphabet=ALPHABET):
    return ''.join(secrets.choice(alphabet) for _ in range(length))
