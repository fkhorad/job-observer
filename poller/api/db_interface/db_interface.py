
from poller.api.db_interface.api_db_sqlite import init_sqlite_db, insert_job, get_new_jobs
from poller.api.db_interface.service_db_fake import get_services
from poller.config import DEF_BATCH

# Change here (+ config) only if not sqlite
def init_db():
    init_sqlite_db()

def get_db():
    return SQLITE_DB()


################################
# sqlite (+ temp JSON interface)
################################

class SQLITE_DB:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def insert_job(self, job_id, service):
        insert_job(job_id, service)

    def get_new_jobs(self, new_jobs_parameters, batch=DEF_BATCH):
        last_seq = new_jobs_parameters['last_seq']
        return get_new_jobs(last_seq, batch)


    # TODO: refactor
    def get_services(self):
        return get_services()