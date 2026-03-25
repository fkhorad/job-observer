# Job Observer
# Copyright (c) 2025 Name Surname
# Licensed under the MIT License. See LICENSE file in the project root.

from fastapi import FastAPI, Depends
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import logging

from observer.scheduler.db_interface.scheduler_db_interface import get_db as get_scheduler_db
from observer.api.db_interface.api_db_interface import get_db as get_api_db
from observer.api.setup import bootstrap, get_api_key


# INIT API
app = FastAPI()
#
bootstrap()
logger = logging.getLogger(__name__)


# Endpoints
@app.get("/health")
def health():

    logger.debug('/health endpoint successfully called')

    with get_scheduler_db(read_only=True) as sched_db:
        heartbeat = sched_db.check_heartbeat()
    return {"API status": "ok", 'Scheduler last heartbeat': heartbeat}


# POST: /add_job --> inserts a new job
class PostJobRequest(BaseModel):
    job_id: str
    service: str
    callback_url: Optional[HttpUrl] = None
#
@app.post("/add_job")
def add_job(req: PostJobRequest):

    logger.debug('/add_job endpoint successfully called')

    with get_api_db() as api_db:
        callback_url = str(req.callback_url) if req.callback_url is not None else None
        api_db.insert_job(req.job_id, req.service, callback_url)

    return {'status': 'accepted'}


# GET: /job_status --> get job(s) status and aux parameter by JOB_ID; in principle it can return more than one (due to absence of service ID) -- TODO: discuss!
@app.get("/job_status")
def get_job_status(job_id: str, service: str):

    logger.debug('/job_status endpoint successfully called')

    with get_scheduler_db(read_only=True) as sched_db:
        jobs = sched_db.get_jobs_by_id(job_id, service)
        return {'jobs': jobs}


# GET: /services --> returns service list (with all configuration parameters)
@app.get("/services")
def get_services():

    logger.debug('/services endpoint successfully called')

    with get_api_db(no_connection=True) as api_db:
        return api_db.get_services_filtered()


# POST: /add_service --> registers a new service
class PostServiceRequest(BaseModel):
    data: Dict[str, Any]
    overwrite: Optional[bool] = False
#
@app.post("/add_services")
def add_services(req: PostServiceRequest, setup_key: str = Depends(get_api_key)):

    logger.debug('/add_services endpoint successfully called')

    with get_api_db(no_connection=True) as api_db:
        return api_db.add_services(req.data, req.overwrite)