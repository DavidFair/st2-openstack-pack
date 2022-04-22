from dataclasses import dataclass
from typing import Optional, Tuple

from enums.ip_version import IPVersion
from enums.network_direction import NetworkDirection
from enums.protocol import Protocol


@dataclass
class SecurityGroupRuleDetails:
    security_group_identifier: str
    project_identifier: str

    direction: NetworkDirection
    ip_version: IPVersion
    protocol: Protocol
    remote_ip_cidr: str

    port_range: Optional[Tuple[int, int]] = None
    rule_name: Optional[str] = None
