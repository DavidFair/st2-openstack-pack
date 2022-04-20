from dataclasses import dataclass
from typing import Optional


@dataclass
class ProjectDetails:
    name: str
    description: str
    is_enabled: bool
    domain_id: Optional[str] = None
