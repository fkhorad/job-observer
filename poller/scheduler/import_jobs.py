
from poller.api.db_interface.api_db_interface import get_db as get_api_db
from poller.scheduler.db_interface.scheduler_db_interface import get_db

def import_jobs():

    with get_db() as sched_db:
        new_jobs_parameters = sched_db.get_new_jobs_parameters()

        with get_api_db() as api_db:
            rows, api_limit_hit = api_db.get_new_jobs(new_jobs_parameters)

        if rows:
            sched_db.insert_jobs(rows)

        due_jobs, scheduler_limit_hit = sched_db.get_due_jobs()
        
        return due_jobs, (api_limit_hit or scheduler_limit_hit)