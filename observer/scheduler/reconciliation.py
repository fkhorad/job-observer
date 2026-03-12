# Job Observer
# Copyright (c) 2025 Name Surname
# Licensed under the MIT License. See LICENSE file in the project root.

import asyncio
import httpx
import logging

from observer.scheduler.db_interface.scheduler_db_interface import get_db
from observer.config import GLOBAL_PSEUDOSERVICE


logger = logging.getLogger(__name__)

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

    try:
        items, items_queued = fetch_items()
    except Exception:
        logger.exception('Problem in fetching items')
        items = []

    logger.info('Items: ' + str(items))

    if not items:
        return
    
    global_semaphore = service_semaphores[GLOBAL_PSEUDOSERVICE]

    async with httpx.AsyncClient() as client:

        async def guarded(item):

            # Skipping items to be done outside the cycle
            local_semaphore = service_semaphores[item.service] # items should be namedtuples or classes including a service class member, which can be set to DUMMY_SERVICE (see db_interface.services_interface) to yield a None Semaphore

            try:
                async with global_semaphore:
                    if local_semaphore is not None:
                        async with local_semaphore:
                            result = await worker_fn(client, item)
                    else:
                        result = await worker_fn(client, item)
                
                return {
                    "item": item,
                    "status": "ok",
                    "result": result,
                }
    
            except Exception as e: #### MMMMMMM
                return {
                    "item": item,
                    "status": "error",
                    "error": str(e),
                }

        tasks = [guarded(item) for item in items]
        dressed_results = await asyncio.gather(*tasks)

    # --- single writer phase ---
    with get_db() as db:
        try:
            apply_results(db, dressed_results)
        except Exception:
            logger.exception('Problem in updating DB')

    return items_queued
