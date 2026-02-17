from datetime import datetime, timedelta, timezone


MAX_BACKOFF = 60 # Centralize

def compute_next_poll(old_state, new_state, unchanged_count):
    now = datetime.now(timezone.utc)

    if new_state != old_state:
        return now + timedelta(seconds=2), 0

    unchanged_count += 1
    delay = min(2 ** unchanged_count, MAX_BACKOFF)
    return now + timedelta(seconds=delay), unchanged_count
