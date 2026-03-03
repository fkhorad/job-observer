import logging

from poller.api.db_interface.api_db_interface import get_db as get_api_db
from poller.scheduler.db_interface.scheduler_db_interface import get_db


logger = logging.getLogger(__name__)

def import_jobs():

    with get_db() as sched_db:
        new_jobs_parameters = sched_db.get_new_jobs_parameters()

        try:
            with get_api_db(read_only=True) as api_db:
                rows, api_limit_hit = api_db.get_new_jobs(new_jobs_parameters)
        except Exception:
            logger.exception('Problem in importing jobs from api.db')
            rows = []
            api_limit_hit = False

        if rows:
            sched_db.insert_jobs(rows)

        due_jobs, scheduler_limit_hit = sched_db.get_due_jobs()
        
        return due_jobs, (api_limit_hit or scheduler_limit_hit)