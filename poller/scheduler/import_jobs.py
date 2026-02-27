
from poller.api.db_interface.db_interface import get_db as get_api_db
from poller.scheduler.db_interface.db_interface import get_db

def import_jobs():

    # TODO: consider if it is best to separate sched_db transactions
    with get_db() as sched_db:
        new_jobs_parameters = sched_db.get_new_jobs_parameters()

        with get_api_db() as api_db:
            rows = api_db.get_new_jobs(new_jobs_parameters)

        for _, job_id, service in rows:
            sched_db.insert_job(job_id, service)

        if rows:
            sched_db.update_new_jobs_parameters(rows)

        return sched_db.get_due_jobs()