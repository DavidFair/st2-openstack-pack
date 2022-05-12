from typing import Optional, List

from openstack.exceptions import ResourceNotFound
from openstack.network.v2.floating_ip import FloatingIP
from openstack.network.v2.network import Network
from openstack.network.v2.rbac_policy import RBACPolicy

from enums.rbac_network_actions import RbacNetworkActions
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_identity import OpenstackIdentity
from structs.network_details import NetworkDetails
from structs.network_rbac import NetworkRbac


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
        rbac_id = self.find_network_rbac(cloud_account, rbac_identifier)
        if not rbac_id:
            return False

        with self._connection_cls(cloud_account) as conn:
            result = conn.network.delete_rbac_policy(rbac_id, ignore_missing=False)
            return result is None
