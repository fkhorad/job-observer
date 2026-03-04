from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class RequestParameters():
    method: str
    url: str
    timeout: float
    status_field: str
    query_params: Dict[str, str] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
