import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path

from poller.config import API_DB as DB


app = FastAPI()

def init_db():
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


init_db()


class JobRequest(BaseModel):
    job_id: str
    service: str


@app.post("/jobs")
def create_job(req: JobRequest):
    print("DB PATH =", Path(DB).resolve())
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO job_requests(job_id, service) VALUES (?,?)",
            (req.job_id, req.service),
        )
    return {"status": "accepted"}
