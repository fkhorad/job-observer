import logging

from observer.config import GLOBAL_PSEUDOSERVICE
from observer.config import DUMMY_SERVICE
from observer.scheduler.poll_logic.service import Service
from observer.config import DEFAULT_SERVICE_TIMEOUT, DEFAULT_SERVICE_MAX_CONCURRENCY
from observer.api.db_interface.api_db_interface import get_db as get_api_db


logger = logging.getLogger(__name__)

RESERVED_NAMES = [GLOBAL_PSEUDOSERVICE, DUMMY_SERVICE]

def import_services():
    with get_api_db(no_connection=True) as api_db:
        services_raw = api_db.get_services()

    services = {}
    for name, cfg in services_raw.items():
        if name in RESERVED_NAMES: # These service names are not allowed and ignored in import
            continue
        services[name] = Service(
            name=name,
            method=cfg["method"],
            url=cfg["url"],
            query_params=cfg.get("query_params", {}),
            body=cfg.get("body", {}),
            static_headers=cfg.get("headers", {}),
            timeout=get_float(name, cfg, "timeout", DEFAULT_SERVICE_TIMEOUT),
            status_field=cfg.get("status_field", "status"),
            terminal_states=set(cfg.get("terminal_states", [])),
            max_concurrency=get_int(name, cfg, "max_concurrency", DEFAULT_SERVICE_MAX_CONCURRENCY),
            auth_type=cfg.get('auth_type'),
            auth_config=cfg.get('auth_config', {})
        )

    return services


def get_int(service_name, config_dict, key, default):
    value = config_dict.get(key)
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f'Using default value for unparsable {key} in {service_name}, value was {value}')
        return default

def get_float(service_name, config_dict, key, default):
    value = config_dict.get(key)
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f'Using default value for unparsable {key} in {service_name}, value was {value}')
        return default
