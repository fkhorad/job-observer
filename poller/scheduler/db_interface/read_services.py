import json

from poller.scheduler.service_dataclass import ServiceDefinition
from poller.config import JSON_SERVICES, DEFAULT_SERVICE_TIMEOUT, DEFAULT_SERVICE_MAX_CONCURRENCY


def read_services(path: str = JSON_SERVICES):
    raw = json.load(path)
    services = {}

    for name, cfg in raw.items():
        services[name] = ServiceDefinition(
            name=name,
            method=cfg["method"],
            url=cfg["url"],
            query_params=cfg.get("query_params", {}),
            body=cfg.get("body", {}),
            headers=cfg.get("headers", {}),
            timeout=cfg.get("timeout", DEFAULT_SERVICE_TIMEOUT),
            status_field=cfg.get("status_field", "status"),
            terminal_states=set(cfg.get("terminal_states", [])),
            max_concurrency=cfg.get("max_concurrency", DEFAULT_SERVICE_MAX_CONCURRENCY),
        )

    return services


# Service constant, to export
SERVICES = read_services()