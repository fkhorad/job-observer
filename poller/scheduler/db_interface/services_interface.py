
from poller.scheduler.services_dataclass import ServiceDefinition
from poller.config import DEFAULT_SERVICE_TIMEOUT, DEFAULT_SERVICE_MAX_CONCURRENCY
from poller.api.db_interface.db_interface import get_db as get_api_db


def import_services():
    with get_api_db() as api_db:
        services_raw = api_db.get_services()

    services = {}
    for name, cfg in services_raw.items():
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
SERVICES = import_services()