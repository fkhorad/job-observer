from typing import NamedTuple
from datetime import datetime


class Job(NamedTuple):
    job_id: str
    service: str
    state: str
    unchanged_count: int
    next_poll_at: datetime
    is_terminal: bool
    callback_url: str
