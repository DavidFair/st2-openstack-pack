from dataclasses import dataclass
from typing import Tuple

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

    port_range: Tuple[str, str]
