import asyncio
import time
import logging

from poller.scheduler.db_interface.services_interface import SERVICES, GLOBAL_PSEUDOSERVICE, DUMMY_SERVICE
from poller.scheduler.db_interface.fetch_items import import_jobs, fetch_callbacks
from poller.scheduler.db_interface.scheduler_db_interface import init_db
from poller.config import SCHEDULER_IDLE_SLEEP, SCHEDULER_BUSY_SLEEP, RUN_ONCE, GLOBAL_CONCURRENCY, LOGGING_LEVEL
from poller.scheduler.reconciliation import run_reconciliation_phase


logger = logging.getLogger(__name__)


def init():
    config_logging()
    init_db()


def config_logging():
    logging.basicConfig(
        level=LOGGING_LEVEL,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# RUN
async def start():
    init()

    # Main loop
    while True:
        logger.info("Scheduler Tick")
        
        start = time.monotonic()

        # TODO: recheck they do belong here
        semaphores = {
            name: asyncio.Semaphore(s.max_concurrency)
            for name, s in SERVICES.items()
        }
        semaphores[GLOBAL_PSEUDOSERVICE] = asyncio.Semaphore(GLOBAL_CONCURRENCY)
        semaphores[DUMMY_SERVICE] = None

        jobs_queued = await run_reconciliation_phase(fetch_items=import_jobs, worker_fn=poll_service, apply_results=update_jobs, service_semaphores=semaphores)

        # then
        callbacks_queued = await run_reconciliation_phase(fetch_items=fetch_callbacks, worker_fn=do_callback, apply_results=update_callbacks, service_semaphores=semaphores)

        if RUN_ONCE: # For debugging only
            break

        if jobs_queued or callbacks_queued:
            await asyncio.sleep(SCHEDULER_BUSY_SLEEP)
        else:
            elapsed = time.monotonic() - start
            await asyncio.sleep(max(SCHEDULER_BUSY_SLEEP, SCHEDULER_IDLE_SLEEP - elapsed))


# Workers
async def poll_service(client, job):
     service = SERVICES.get(job[1])
     return await service.poll(client, job)

def update_jobs(db, dressed_results):
    db.update_jobs(dressed_results)


async def do_callback(client, callback):
    callback.do_callback(client)

def update_callbacks(db, dressed_results):
    db.update_callbacks(dressed_results)


if __name__ == "__main__":
    asyncio.run(start())