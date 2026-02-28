import asyncio
import httpx

from poller.scheduler.db_interface.services_interface import SERVICES
from poller.scheduler.import_jobs import import_jobs
from poller.scheduler.db_interface.db_interface import init_db, get_db
from poller.config import SCHEDULER_INTERVAL, RUN_ONCE, GLOBAL_CONCURRENCY
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("worker")


# Heartbeat function
async def reconciliation_cycle():

    jobs = import_jobs()

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
            for dressed_result in dressed_results:
                try:
                    db.update_job(dressed_result['result'])
                except Exception as err:
                    logger.error(err)

def init():
    # Could contain more init steps
    init_db()


# RUN
async def start():

    init()

    # For debugging
    if RUN_ONCE:
        await reconciliation_cycle()
        return

    # Main loop
    while True:
        logger.info("Scheduler Tick")
        await reconciliation_cycle()
        await asyncio.sleep(SCHEDULER_INTERVAL)


if __name__ == "__main__":
    asyncio.run(start())