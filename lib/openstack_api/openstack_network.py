import ipaddress
import random
from typing import Optional, List

from openstack.exceptions import ResourceNotFound
from openstack.network.v2.floating_ip import FloatingIP
from openstack.network.v2.network import Network
from openstack.network.v2.rbac_policy import RBACPolicy
from openstack.network.v2.router import Router
from openstack.network.v2.subnet import Subnet

from enums.rbac_network_actions import RbacNetworkActions
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_identity import OpenstackIdentity
from structs.network_details import NetworkDetails
from structs.network_rbac import NetworkRbac
from structs.router_details import RouterDetails


class OpenstackNetwork(OpenstackWrapperBase):
    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(connection_cls)

    def allocate_floating_ips(
        self, cloud_account, network_identifier, project_identifier, number_to_create
    ) -> List[FloatingIP]:
        """
        Allocates floating IPs to a given project
        :param cloud_account: The account from the clouds configuration to use
        :param network_identifier: ID or Name of network to allocate from,
        :param project_identifier: ID or Name of project to allocate to,
        :param number_to_create: Number of floating ips to create
        :return: List of all allocated floating IPs
        """
        project = self._identity_api.find_mandatory_project(
            cloud_account, project_identifier
        )
        network = self.find_network(cloud_account, network_identifier)
        if not network:
            raise ItemNotFoundError("The requested network was not found")

        created: List[FloatingIP] = []
        with self._connection_cls(cloud_account) as conn:
            for _ in range(number_to_create):
                created.append(
                    conn.network.create_ip(
                        project_id=project.id, floating_network_id=network.id
                    )
                )
        return created

    def get_floating_ip(self, cloud_account: str, ip_addr: str) -> Optional[FloatingIP]:
        ip_addr = ip_addr.strip()
        if not ip_addr:
            raise MissingMandatoryParamError("An IP address is required")

        with self._connection_cls(cloud_account) as conn:
            try:
                return conn.network.get_ip(ip_addr)
            except ResourceNotFound:
                return None

    def find_network(
        self, cloud_account: str, network_identifier: str
    ) -> Optional[Network]:
        """
        Finds a given network using the name or ID
        :param cloud_account: The associated clouds.yaml account
        :param network_identifier: The ID or name to search for
        :return: The found network or None
        """
        network_identifier = network_identifier.strip()
        if not network_identifier:
            raise MissingMandatoryParamError("A network identifier is required")

        with self._connection_cls(cloud_account) as conn:
            return conn.network.find_network(network_identifier, ignore_missing=True)

    def search_network_rbacs(
        self, cloud_account: str, project_identifier: str
    ) -> List[RBACPolicy]:
        """
        Finds a given RBAC network policy associated with a project
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The name or Openstack ID of the project the policy applies to
        :return: A list of found RBAC policies for the given project
        """
        project = self._identity_api.find_mandatory_project(
            cloud_account, project_identifier
        )

        with self._connection_cls(cloud_account) as conn:
            return list(conn.network.rbac_policies(project_id=project.id))

    def create_network(
        self, cloud_account: str, details: NetworkDetails
    ) -> Optional[Network]:
        """
        Creates a network for a given project
        :param cloud_account: The clouds entry to use
        :param details: A struct containing all details related to this new network
        :return: A Network object, or None
        """
        details.name = details.name.strip()
        if not details.name:
            raise MissingMandatoryParamError("A network name is required")

        project = self._identity_api.find_mandatory_project(
            cloud_account, details.project_identifier
        )

        with self._connection_cls(cloud_account) as conn:
            return conn.network.create_network(
                project_id=project.id,
                name=details.name,
                description=details.description,
                provider_network_type=details.provider_network_type.value.lower(),
                is_port_security_enabled=details.port_security_enabled,
                is_router_external=details.has_external_router,
            )

    @staticmethod
    def _parse_rbac_action(action: RbacNetworkActions) -> str:
        """
        Parses the given RBAC enum into an Openstack compatible string
        """
        # This can be replaced with match case when we're Python 3.10+
        if action is RbacNetworkActions.SHARED:
            return "access_as_shared"
        if action is RbacNetworkActions.EXTERNAL:
            return "access_as_external"
        raise KeyError("Unknown RBAC action")

    def create_network_rbac(
        self, cloud_account: str, rbac_details: NetworkRbac
    ) -> RBACPolicy:
        """
        Creates an RBAC policy for the given network
        :param cloud_account: The clouds.yaml account to use
        :param rbac_details: The details associated with the new policy
        :return: The RBAC Policy if it was created, else None
        """
        network = self.find_network(
            cloud_account, network_identifier=rbac_details.network_identifier
        )
        if not network:
            raise ItemNotFoundError("The specified network was not found")

        project = self._identity_api.find_mandatory_project(
            cloud_account, project_identifier=rbac_details.project_identifier
        )

        with self._connection_cls(cloud_account) as conn:
            return conn.network.create_rbac_policy(
                object_id=network.id,
                # We only support network RBAC policies at the moment
                object_type="network",
                target_project_id=project.id,
                action=self._parse_rbac_action(rbac_details.action),
            )

    def delete_network(self, cloud_account: str, network_identifier: str) -> bool:
        """
        Deletes the specified network
        :param cloud_account: The associated credentials to use
        :param network_identifier: The name or Openstack ID to use
        :return: True if deleted, else False
        """
        network = self.find_network(cloud_account, network_identifier)
        if not network:
            return False

        with self._connection_cls(cloud_account) as conn:
            result = conn.network.delete_network(network, ignore_missing=False)
            return result is None

    def delete_network_rbac(self, cloud_account: str, rbac_identifier: str) -> bool:
        """
        Deletes the specified network
        :param cloud_account: The associated credentials to use
        :param rbac_identifier: The name or Openstack ID to use
        :return: True if deleted, else False
        """
        raise NotImplementedError("Pending better RBAC search")
        rbac_id = self.find_network_rbac(cloud_account, rbac_identifier)
        if not rbac_id:
            return False

        with self._connection_cls(cloud_account) as conn:
            result = conn.network.delete_rbac_policy(rbac_id, ignore_missing=False)
            return result is None

    def create_router(self, cloud_account: str, details: RouterDetails) -> Router:
        """
        Creates a router for the given project without any internal interfaces
        :param cloud_account: The associated credentials to use
        :param details: The details of the router to create
        """
        project = self._identity_api.find_mandatory_project(
            cloud_account, details.project_identifier
        )
        external_network = self.find_network(cloud_account, details.external_gateway)
        if not external_network:
            raise ItemNotFoundError("The external network specified was not found")

        with self._connection_cls(cloud_account) as conn:
            return conn.network.create_router(
                project_id=project.id,
                name=details.router_name,
                description=details.router_description,
                external_gateway_info={"network_id": external_network.id},
                is_distributed=details.is_distributed,
                is_ha=details.is_ha,
            )

    def get_router(
        self, cloud_account: str, project_identifier: str, router_identifier: str
    ) -> Optional[Router]:
        """
        Returns a given router found from the given attributes
        :param cloud_account: The associated credentials to use
        :param project_identifier: The project name or ID to search in
        :param router_identifier: The router name or ID to get
        """
        project = self._identity_api.find_mandatory_project(
            cloud_account, project_identifier
        )

        with self._connection_cls(cloud_account) as conn:
            return conn.network.find_router(
                name_or_id=router_identifier, project_id=project.id, ignore_missing=True
            )

    def get_used_subnet_nets(
        self, cloud_account: str, network_identifier: str
    ) -> List[ipaddress.IPv4Network]:
        """
        Gets the subnets associated with a given network
        :param cloud_account: The associated credentials to use
        :param network_identifier: The network to search
        :return: A list of found network addresses
        """
        network = self.find_network(cloud_account, network_identifier)
        if not network:
            raise ItemNotFoundError("The network specified was not found")

        with self._connection_cls(cloud_account) as conn:
            subnets = [
                subnet.gateway_ip
                for subnet in conn.network.subnets(network_id=network.id)
            ]

        # Force to a /24 network
        return [ipaddress.ip_network(i + "/24", strict=False) for i in subnets]

    def select_random_subnet(
        self, cloud_account: str, network_identifier: str
    ) -> ipaddress.IPv4Network:
        """
        Selects a random subnet from the given network that isn't used
        :param cloud_account: The associated credentials to use
        :param network_identifier: The network to search
        :return: A randomly selected subnet
        """
        avail = [ipaddress.ip_network(f"192.168.{i}.0/24") for i in range(1, 255)]

        used_subnets = self.get_used_subnet_nets(cloud_account, network_identifier)
        avail = [i for i in avail if i not in used_subnets]
        if not avail:
            raise ItemNotFoundError("No available subnets")
        return random.choice(avail)

    def create_subnet(
        self,
        cloud_account: str,
        network: str,
        subnet_name: str,
        subnet_description: str,
        dhcp_enabled: bool,
    ) -> Subnet:
        """
        Adds a new subnet with a randomly selected 192.168.x.0/24 to a given network
        :param cloud_account: The associated credentials to use
        :param network: The network to add the new subnet to
        :param subnet_name: The new subnet name
        :param subnet_description: The new subnet description
        :param dhcp_enabled: Whether to enable DHCP on the new subnet
        :return: The newly created subnet object
        """
        network = self.find_network(cloud_account, network)
        if not network:
            raise ItemNotFoundError("The network specified was not found")

        selected_subnet = self.select_random_subnet(cloud_account, network.id)
        hosts = [str(i) for i in selected_subnet.hosts()]
        # Check our first entry is the gateway
        assert hosts[0].endswith(".1")

        with self._connection_cls(cloud_account) as conn:
            return conn.network.create_subnet(
                ip_version=4,
                network_id=network.id,
                # Reserve the first 10 addresses from DHCP allocation
                allocation_pools=[{"start": hosts[10], "end": hosts[-1]}],
                cidr=str(selected_subnet),
                gateway_ip=hosts[0],
                name=subnet_name,
                description=subnet_description,
                is_dhcp_enabled=dhcp_enabled,
            )
