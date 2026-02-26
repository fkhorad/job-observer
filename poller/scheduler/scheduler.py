import asyncio
import httpx

from poller.scheduler.db_interface.read_services import SERVICES
from poller.scheduler.http_client import fetch_status
from poller.scheduler.poll_logic.compute_polls import compute_next_poll
from poller.scheduler.import_jobs import import_jobs
from poller.scheduler.db_interface.db_interface import init_db, get_db
from poller.config import SCHEDULER_INTERVAL, RUN_ONCE


async def poll_service(db, client, job):

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

    # DB update
    db.update_job(job_id, new_state, unchanged_count, next_poll, is_terminal)


# Heartbeat function
async def reconciliation_cycle():

    db = get_db()

    import_jobs(db)

    jobs = db.get_due_jobs()

    async with httpx.AsyncClient() as client:
        tasks = []
        semaphores = {
            name: asyncio.Semaphore(s.max_concurrency)
            for name, s in SERVICES.items()
        }

        async def guarded(job):
            service = SERVICES.get(job[1])
            if service is None:
                return
            
            async with semaphores[service.name]:
                await poll_service(db, client, job)

        for job in jobs:
            tasks.append(guarded(job))

        await asyncio.gather(*tasks)

    db.clean()


# RUN

def init():
    init_db()


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


def run():
    asyncio.run(start())

if __name__ == "__main__":
    run()