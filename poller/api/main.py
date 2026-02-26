from fastapi import FastAPI
from pydantic import BaseModel

from poller.scheduler.db_interface.db_interface import get_db as get_scheduler_db
from poller.api.db_interface.db_interface import init_db, get_db as get_api_db


# INIT API
app = FastAPI()
#
init_db()



# Endpoints

# POST: /add_job --> inserts a new job
class PostJobRequest(BaseModel):
    job_id: str
    service: str
#
@app.post("/add_job")
def add_job(req: PostJobRequest):

    api_db = get_api_db()
    api_db.insert_job(req.job_id, req.service)

    return {'status': 'accepted'}


# GET: /job_status --> get job(s) status and aux parameter by JOB_ID; in principle it can return more than one (due to absence of service ID) -- TODO: discuss!
@app.get("/job_status")
def get_job_status(job_id: str):
    sched_db = get_scheduler_db()
    jobs = sched_db.get_jobs_by_id(job_id)
    return {'jobs': jobs}


# GET: /services --> returns service list (with all configuration parameters)
@app.get("/services")
def get_services():
    api_db = get_api_db()
    return api_db.get_services()


# TODO: add POST to update service list