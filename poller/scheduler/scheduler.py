import asyncio
import sqlite3
import httpx
from datetime import datetime, timezone

from poller.define_services import SERVICES
from poller.scheduler.http_client import fetch_status
from poller.scheduler.poll_computation import compute_next_poll
from poller.scheduler.importer import import_jobs
from poller.scheduler.scheduler_db import init_scheduler_db, get_due_jobs
from poller.config import API_DB, SCHEDULER_DB as SCHED_DB, SCHEDULER_INTERVAL


SCHEDULER_INTERVAL = 2

async def poll_service(con, client, job):
    job_id, service_name, old_state, unchanged = job
    service = SERVICES[service_name]

    new_state = await fetch_status(client, service, job_id)
    if new_state is None:
        return

    terminal = new_state in service.terminal_states
    next_poll, unchanged = compute_next_poll(old_state, new_state, unchanged)

    con.execute("""
        UPDATE job_state
        SET observed_state=?,
            unchanged_count=?,
            next_poll_at=?,
            is_terminal=?,
            updated_at=?
        WHERE job_id=?
    """, (
        new_state,
        unchanged,
        next_poll.isoformat(),
        int(terminal),
        datetime.now(timezone.utc).isoformat(),
        job_id
    ))


async def reconciliation_cycle():
    api_con = sqlite3.connect(API_DB)
    con = sqlite3.connect(SCHED_DB)

    import_jobs(api_con, con)

    jobs = get_due_jobs(con)

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
                await poll_service(con, client, job)

        for job in jobs:
            tasks.append(guarded(job))

        await asyncio.gather(*tasks)

    con.commit()
    con.close()
    api_con.close()


async def loop():
    init_scheduler_db()
    while True:
        await reconciliation_cycle()
        await asyncio.sleep(SCHEDULER_INTERVAL)


def run():
    asyncio.run(loop())


def run_once():
    asyncio.run(reconciliation_cycle())


if __name__ == "__main__":
    run()