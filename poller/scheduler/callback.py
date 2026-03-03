from dataclasses import dataclass, replace
from datetime import datetime, timedelta

from poller.general_helpers import utcnow
from poller.config import CALLBACK_RETRIES


DELIVERED = 'delivered'
PENDING = 'pending'
FAILED = 'failed'

@dataclass
class Callback:
    id: int
    job_id: str
    callback_url: str
    job_terminal_state: str
    callback_state: str
    retry_count: int
    created_at: datetime
    next_attempt_at: datetime
    last_error: str
    delivered_at: datetime
    service: str


    async def do_callback(self, client):

        payload = {'job_id': self.job_id, 'status': self.job_terminal_state, 'end_confirmed_at': self.created_at}

        response = await client.post(self.callback_url, json=payload)

        now = utcnow()

        if 200 <= response.status_code < 300:
            return replace(self, callback_state=DELIVERED, next_attempt_at=None, delivered_at=now)

        new_retry_count = self.retry_count + 1
        if (response.status_code >= 500 or response.status_code == 429) and new_retry_count<CALLBACK_RETRIES:
            backoff_seconds = 2**new_retry_count # Simple backoff logic
            next_attempt_at = now + timedelta(seconds=backoff_seconds)
            return replace(self, callback_state=PENDING, retry_count=new_retry_count, next_attempt_at=next_attempt_at, last_error=f'HTTP {response.status_code}')

        return replace(self, retry_count=new_retry_count, callback_state=FAILED, next_attempt_at=None, last_error=f'HTTP {response.status_code}')
    
