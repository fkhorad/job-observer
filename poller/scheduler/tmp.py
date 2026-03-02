import asyncio
import httpx

from poller.scheduler.db_interface.scheduler_db_interface import get_db
from poller.config import GLOBAL_CONCURRENCY




async def run_reconciliation_phase(
    *,
    fetch_items,          # sync function → list[Item]
    worker_fn,            # async fn(client, item) → result dict
    apply_results,        # sync fn(db, results)
    service_semaphores    # defined outside the cycle, they include the global one
):
    """
    Generic reconciliation phase:

    1. Fetch items
    2. Async bounded processing
    3. Barrier
    4. Single short DB write phase
    """

    items, items_queued = fetch_items()

    # Logging?

    if not items:
        return
    
    global_semaphore = asyncio.Semaphore(GLOBAL_CONCURRENCY)

    async with httpx.AsyncClient() as client:

        async def guarded(item):

            # Skipping items to be done outside the cycle
            local_semaphore = service_semaphores(item[1]) # item must always include a 'fake' service, which has a None semaphore

            try:
                async with global_semaphore:
                    if local_semaphore is not None:
                        async with local_semaphore:
                            result = await worker_fn(client, item)
                    else:
                        result = await worker_fn(client, item)
                
                return {
                    "job": item,
                    "status": "ok",
                    "result": result,
                }
    
            except Exception as e:
                return {
                    "item": item,
                    "status": "error",
                    "error": str(e),
                }

        tasks = [guarded(item) for item in items]
        results = await asyncio.gather(*tasks)

    # --- single writer phase ---
    with get_db() as db:
        try:
            apply_results(db, results)
        except Exception as err:
            pass
            # OR LOG...

    return items_queued

######################################


async def callback_worker(client, callback):

    response = await client.post(
        callback.callback_url,
        json=callback.payload,
    )

    if 200 <= response.status_code < 300:
        return {
            "id": callback.id,
            "status": "delivered",
        }

    if response.status_code >= 500 or response.status_code == 429:
        return {
            "url": callback.url,
            "status": "retry",
            "error": f"HTTP {response.status_code}",
        }

    return {
        "url": callback.url,
        "status": "failed_permanent",
        "error": f"HTTP {response.status_code}",
    }


## Need a 'callback' object. TRY to use URL as ID.