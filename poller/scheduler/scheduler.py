import asyncio
import httpx

from poller.scheduler.db_interface.services_interface import SERVICES
from poller.scheduler.http_client import fetch_status
from poller.scheduler.poll_logic.compute_polls import compute_next_poll
from poller.scheduler.import_jobs import import_jobs
from poller.scheduler.db_interface.db_interface import init_db, get_db
from poller.config import SCHEDULER_INTERVAL, RUN_ONCE, GLOBAL_CONCURRENCY


async def poll_service(client, job):

    job_id, service_name, old_state, unchanged_count = job
    service = SERVICES[service_name]

    # HTTP request to external service
    new_state = await fetch_status(client, service, job_id)
    if new_state is None: # None here means request failed; exit without updating job
        return

    # Update job

    # Get update params
    if new_state != old_state:
        unchanged_count = 0
    else:
        unchanged_count += 1
    #
    next_poll = compute_next_poll(unchanged_count)
    #
    is_terminal = new_state in service.terminal_states

    return {'job_id': job_id, 'service': service_name, 'new_state': new_state, 'unchanged_count': unchanged_count, 'next_poll': next_poll, 'is_terminal': is_terminal}


# Heartbeat function
async def reconciliation_cycle():

    jobs = import_jobs()

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
                        result = await poll_service(client, job)

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
                except:
                    pass

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
        await reconciliation_cycle()
        await asyncio.sleep(SCHEDULER_INTERVAL)


if __name__ == "__main__":
    asyncio.run(start())