# Job Observer
# Copyright (c) 2025 Name Surname
# Licensed under the MIT License. See LICENSE file in the project root.

from datetime import timedelta
import random

from observer.config import MIN_BACKOFF, MAX_BACKOFF
from observer.general_helpers import utcnow


def compute_next_poll(unchanged_count):

    now = utcnow()
    delay = get_delay(unchanged_count)
    return now + timedelta(seconds=delay)


def get_delay(unchanged_count):

    # Simple delay model: bounded exponential backoff
    delay = min(MIN_BACKOFF ** unchanged_count, MAX_BACKOFF)

    # Jitter (should limit job clustering after downtime)
    delay += random.uniform(0, delay * 0.1)
    
    return delay


