# Job Observer
# Copyright (c) 2025 Name Surname
# Licensed under the MIT License. See LICENSE file in the project root.

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Set, Optional

from observer.scheduler.http_client import fetch_status
from observer.scheduler.poll_logic.compute_polls import compute_next_poll
from observer.config import DEFAULT_SERVICE_TIMEOUT as DEF_TIMEOUT, DEFAULT_SERVICE_MAX_CONCURRENCY as DEF_MAX_CONCURRENCY, DEFAULT_STATUS_FIELD as DEF_STATUS_FIELD
from observer.scheduler.dtos.job import Job
from observer.scheduler.dtos.request_parameters import RequestParameters


@dataclass
class Service:
    # --------------------
    # Static configuration
    # --------------------
    name: str
    method: str
    url: str
    query_params: Dict[str, str] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    static_headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = DEF_TIMEOUT
    status_field: str = DEF_STATUS_FIELD
    terminal_states: Set[str] = field(default_factory=set)
    max_concurrency: int = DEF_MAX_CONCURRENCY
    description: Optional[str] = None


    # ------------------------------
    # Optional authentication config
    # ------------------------------
    auth_type: Optional[str] = None
    auth_config: Dict[str, Any] = field(default_factory=dict)


    # --------------------------
    # Runtime state (NOT config)
    # --------------------------
    _token: Optional[str] = field(default=None, init=False, repr=False)
    _expires_at: Optional[float] = field(default=None, init=False, repr=False)
    _auth_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)


    # ============================================================
    # Public API used by reconciliation loop
    # ============================================================
    async def poll(self, client, job: Job): # TODO: consider 'reinforcing' timeout (it is perhaps too low-level now, doesn't include the wrapping)
        """
        Main polling entry point.
        Called by reconciliation loop.
        """

        job_id = job.job_id
        request_parameters = await self._build_request(client, job.job_id)

        status_response = await fetch_status(client, request_parameters)

        if not status_response:
            return None # In case of None response, no update is performed

        if status_response["response_status"] == "OK":
            new_state = status_response["service_status"]

        elif status_response["response_status"] == "404":
            new_state = "NOT_FOUND"

        else:
            # Transport failure or unknown condition
            return None

        return self._reconcile_state(
            job_id=job_id,
            old_state=job.state,
            unchanged_count=job.unchanged_count,
            new_state=new_state,
            callback_url=job.callback_url
        )

    async def _build_request(self, client, job_id):
        await self._ensure_token(client)

        headers = dict(self.static_headers)

        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        return RequestParameters( method=self.method, url=render(self.url, job_id), query_params=render(self.query_params, job_id), body=render(self.body, job_id) if self.method != "GET" else None, timeout=self.timeout, status_field=self.status_field, headers=headers )


    # ============================================================
    # State reconciliation logic (policy)
    # ============================================================

    def _reconcile_state(self, job_id, old_state, unchanged_count, new_state, callback_url):
        """
        Encapsulates job state transition policy.
        """

        if new_state != old_state:
            unchanged_count = 0
        else:
            unchanged_count += 1

        next_poll_at = compute_next_poll(unchanged_count)

        is_terminal = (
            new_state in self.terminal_states
            or (new_state == "NOT_FOUND" and unchanged_count >= 3)
        )

        return Job(job_id=job_id, service=self.name, state=new_state, unchanged_count=unchanged_count, next_poll_at=next_poll_at, is_terminal=is_terminal, callback_url=callback_url)


    # ============================================================
    # Authentication lifecycle
    # ============================================================

    async def _ensure_token(self, client):
        if not self.auth_type:
            return

        if self._token and not self._is_token_expired():
            return

        async with self._auth_lock:
            if self._token and not self._is_token_expired():
                return

            token, expires_in = await self._fetch_token(client)
            self._token = token
            self._expires_at = time.time() + expires_in


    def _is_token_expired(self) -> bool:
        if not self._expires_at:
            return True
        return time.time() >= self._expires_at - 5  # 5s safety margin


    async def _fetch_token(self, client):
        """
        Fetches a new token based on auth_type.
        Minimal example: client_credentials_basic.
        """
        if self.auth_type == "client_credentials_basic":
            token_url = self.auth_config["token_url"]
            client_id = self.auth_config["client_id"]
            client_secret = self.auth_config["client_secret"]

            response = await client.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                timeout=self.timeout,
            )

            response.raise_for_status()
            payload = response.json()

            return payload["access_token"], payload.get("expires_in", 3600)

        elif self.auth_type == "client_credentials_headers":
            token_url = self.auth_config["token_url"]

            response = await client.post(
                token_url,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {self.auth_config['client_credentials']}"
                },
                data={
                    "grant_type": "client_credentials"
                },
                timeout=self.timeout
            )

            response.raise_for_status()
            payload = response.json()

            return payload["access_token"], payload["expires_in"]


        raise RuntimeError(f"Unsupported auth_type: {self.auth_type}")
    

# Helper for request parameters definition
def render(v, job_id: str):
    if isinstance(v, str):
        return v.replace("{job_id}", job_id)
    if isinstance(v, dict):
        return {k: render(val, job_id) for k, val in v.items()}
    if isinstance(v, list):
        return [render(x, job_id) for x in v]
    return v
