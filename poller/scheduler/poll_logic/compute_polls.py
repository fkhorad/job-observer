from datetime import timedelta

from poller.config import MIN_BACKOFF, MAX_BACKOFF
from poller.general_helpers import utcnow


def compute_next_poll(unchanged_count):

    now = utcnow()
    delay = get_delay(unchanged_count)
    return now + timedelta(seconds=delay), unchanged_count


def get_delay(unchanged_count):
    # Simple delay model: delay increases exponentially with unchanged count, up to max
    return min(MIN_BACKOFF ** unchanged_count, MAX_BACKOFF)

