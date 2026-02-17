from fastapi import FastAPI
import random


app = FastAPI()

@app.get("/status/{job_id}")
def status(job_id: str):
    return {"status": random.choice(["pending", "running", "done"])}
