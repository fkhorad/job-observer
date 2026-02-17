import httpx

from poller.scheduler.render import render


async def fetch_status(client, service, job_id):
    try:
        r = await client.request(
            service.method,
            render(service.url, job_id),
            params=render(service.query_params, job_id),
            json=render(service.body, job_id) if service.method != "GET" else None,
            headers=render(service.headers, job_id),
            timeout=service.timeout,
        )
        r.raise_for_status()
        return r.json().get(service.status_field)
    except Exception:
        return None
