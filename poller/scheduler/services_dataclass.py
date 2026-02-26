from dataclasses import dataclass, field
from typing import Dict, Any, Set
from poller.config import DEFAULT_SERVICE_TIMEOUT as DEF_TIMEOUT, DEFAULT_SERVICE_MAX_CONCURRENCY as MAX_CONCURRENCY, DEFAULT_STATUS_FIELD as DEF_STATUS_FIELD


@dataclass
class ServiceDefinition:
    name: str
    method: str
    url: str
    query_params: Dict[str, str] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = DEF_TIMEOUT
    status_field: str = DEF_STATUS_FIELD
    terminal_states: Set[str] = field(default_factory=set)
    max_concurrency: int = MAX_CONCURRENCY
