import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Set

from poller.config import CLIENT_TIMEOUT as TIMEOUT, BASE_DIR
### Add other constants similarly


@dataclass
class ServiceDefinition:
    name: str
    method: str
    url: str
    query_params: Dict[str, Any] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = TIMEOUT
    status_field: str = "status"
    terminal_states: Set[str] = field(default_factory=set)
    max_concurrency: int = 10


def load_services(path: str = BASE_DIR/'services.json'):
    raw = json.loads(Path(path).read_text())
    services = {}

    for name, cfg in raw.items():
        services[name] = ServiceDefinition(
            name=name,
            method=cfg["method"],
            url=cfg["url"],
            query_params=cfg.get("query_params", {}),
            body=cfg.get("body", {}),
            headers=cfg.get("headers", {}),
            timeout=cfg.get("timeout", 2.0),
            status_field=cfg.get("status_field", "status"),
            terminal_states=set(cfg.get("terminal_states", [])),
            max_concurrency=cfg.get("max_concurrency", 10),
        )

    return services


SERVICES = load_services()