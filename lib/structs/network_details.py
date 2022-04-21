from dataclasses import dataclass

from enums.network_providers import NetworkProviders


@dataclass
class NetworkDetails:
    name: str
    description: str
    project_identifier: str
    provider_network_type: NetworkProviders
    port_security_enabled: bool
    has_external_router: bool
