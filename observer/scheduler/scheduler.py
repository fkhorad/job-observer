# Job Observer
# Copyright (c) 2025 Name Surname
# Licensed under the MIT License. See LICENSE file in the project root.

import asyncio
import time
import logging

from observer.general_helpers import config_logging
from observer.scheduler.db_interface.services_interface import import_services
from observer.scheduler.db_interface.fetch_items import import_jobs, fetch_callbacks
from observer.scheduler.db_interface.scheduler_db_interface import check_db, get_db
from observer.config import DUMMY_SERVICE, GLOBAL_PSEUDOSERVICE, SCHEDULER_IDLE_SLEEP, SCHEDULER_BUSY_SLEEP, RUN_ONCE, GLOBAL_CONCURRENCY
from observer.scheduler.reconciliation import run_reconciliation_phase


# Logging
LOGGING_CONF = config_logging()
logging.basicConfig(level=LOGGING_CONF['logging_level'], format=LOGGING_CONF['logging_format'])
logger = logging.getLogger(__name__)

SERVICES = {}
def init():

    try:
        global SERVICES
        SERVICES = import_services()
        check_db()
    except:
        logger.exception('Crushed on init')
        raise


# RUN
async def start():

    init()

    # Main loop
    while True:
        logger.debug("Scheduler Tick")
        
        with get_db() as db:
            db.upsert_heartbeat()

        start = time.monotonic()

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
    return await callback.do_callback(client)

def update_callbacks(db, dressed_results):
    db.update_callbacks(dressed_results)


if __name__ == "__main__":
    asyncio.run(start())