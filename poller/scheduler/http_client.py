import httpx
from poller.scheduler.dtos.request_parameters import RequestParameters


async def fetch_status(client, request_parameters: RequestParameters):
    try:
        r = await client.request(
            request_parameters.method,
            request_parameters.url,
            params=request_parameters.query_params,
            json=request_parameters.body,
            headers=request_parameters.headers,
            timeout=request_parameters.timeout,
        )
        r.raise_for_status()
        return {'response_status': 'OK', 'service_status': r.json().get(request_parameters.status_field)}
    
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        return {'response_status': str(status_code), 'service_status': None}

