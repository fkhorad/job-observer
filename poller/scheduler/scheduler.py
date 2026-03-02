import asyncio
import httpx
import time
import logging

from poller.scheduler.db_interface.services_interface import SERVICES
from poller.scheduler.import_jobs import import_jobs
from poller.scheduler.db_interface.scheduler_db_interface import init_db, get_db
from poller.config import SCHEDULER_IDLE_SLEEP, SCHEDULER_BUSY_SLEEP, RUN_ONCE, GLOBAL_CONCURRENCY
from poller.scheduler.tmp import run_reconciliation_phase


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("worker")


# Heartbeat function
async def reconciliation_cycle():

    jobs, jobs_queued = import_jobs()

    logger.info('JOBS: ' + str(jobs))

    semaphores = {
        name: asyncio.Semaphore(s.max_concurrency)
        for name, s in SERVICES.items()
    }
    global_semaphore = asyncio.Semaphore(GLOBAL_CONCURRENCY)

    async with httpx.AsyncClient() as client:
        tasks = []

        async def guarded(job):
            service = SERVICES.get(job[1])
            if service is None:
                return {
                    "job": job,
                    "status": "skipped",
                    "reason": "unknown service",
                }
        
            try:
                async with global_semaphore:
                    async with semaphores[service.name]:
                        result = await service.poll(client, job)

                return {
                    "job": job,
                    "status": "ok",
                    "result": result,
                }

            except Exception as e:
                return {
                    "job": job,
                    "status": "error",
                    "error": str(e),
                }

        tasks = [guarded(job) for job in jobs]
        dressed_results = await asyncio.gather(*tasks)

        # DB update
        with get_db() as db:
            try:
                db.update_jobs(dressed_results)
            except Exception as err:
                logger.error(err)

        return jobs_queued

def init():
    # Could eventually be expanded to contain more init steps
    init_db()


# RUN
async def start():

    init()

    # For debugging only
    if RUN_ONCE:
        await reconciliation_cycle()
        return

    # Main loop
    while True:
        logger.info("Scheduler Tick")
        
        start = time.monotonic()

        # TODO: recheck they do belong here
        semaphores = {
            name: asyncio.Semaphore(s.max_concurrency)
            for name, s in SERVICES.items()
        }
        semaphores['#GLOBAL_SEMAPHORE#'] = asyncio.Semaphore(GLOBAL_CONCURRENCY)

        #jobs_queued = await reconciliation_cycle()
        jobs_queued = await run_reconciliation_phase(fetch_items=import_jobs, worker_fn=poll_service, apply_results=update_jobs, service_semaphores=semaphores)

        # then
        # callbacks_queued = await run_reconciliation_phase(fetch_items=fetch_callbacks, worker_fn=do_callback, apply_results=update_callbacks, service_semaphores=semaphores)

        if jobs_queued: # ... or callbacks_queued
            await asyncio.sleep(SCHEDULER_BUSY_SLEEP)
        else:
            elapsed = time.monotonic() - start
            await asyncio.sleep(max(SCHEDULER_BUSY_SLEEP, SCHEDULER_IDLE_SLEEP - elapsed))


# "Workers"
def poll_service(client, job):
     service = SERVICES.get(job[1])
     service.poll(client, job)

def update_jobs(db, dressed_results):
    db.update_jobs(dressed_results)


if __name__ == "__main__":
    asyncio.run(start())