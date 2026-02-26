
from poller.api.db_interface.api_db_sqlite import init_sqlite_db, insert_job
from poller.api.db_interface.service_db_fake import get_services


# Change here (+ config) only if not sqlite
def init_db():
    init_sqlite_db()

def get_db():
    return SQLITE_DB()


################################
# sqlite (+ temp JSON interface)
################################

class SQLITE_DB:
    def __init__(self):
        pass

    def insert_job(job_id, service):
        insert_job(job_id, service)

    # TODO: refactor
    def get_services():
        return