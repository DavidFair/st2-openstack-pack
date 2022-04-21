from typing import Optional

from openstack.network.v2.network import Network
from openstack.network.v2.rbac_policy import RBACPolicy

from enums.rbac_network_actions import RbacNetworkActions
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_connection import OpenstackConnection
from openstack_identity import OpenstackIdentity
from structs.network_details import NetworkDetails
from structs.network_rbac import NetworkRbac


class OpenstackNetwork:
    @staticmethod
    def find_network(cloud_account: str, network_identifier: str) -> Optional[Network]:
        """
        Finds a given network using the name or ID
        :param cloud_account: The associated clouds.yaml account
        :param network_identifier: The ID or name to search for
        :return: The found network or None
        """
        network_identifier = network_identifier.strip()
        if not network_identifier:
            raise MissingMandatoryParamError("A network identifier is required")

        with OpenstackConnection(cloud_account) as conn:
            return conn.network.find_network(network_identifier, ignore_missing=True)

    @staticmethod
    def find_network_rbac(
        cloud_account: str, rbac_identifier: str
    ) -> Optional[RBACPolicy]:
        """
        Finds a given RBAC network policy
        :param cloud_account: The associated clouds.yaml account
        :param rbac_identifier: The name or Openstack ID of the policy
        :return: The RBACPolicy object or None
        """
        rbac_identifier = rbac_identifier.strip()
        if not rbac_identifier:
            raise MissingMandatoryParamError("A RBAC name or ID is required")

        with OpenstackConnection(cloud_account) as conn:
            return conn.network.find_rbac_policy(rbac_identifier, ignore_missing=True)

    @staticmethod
    def create_network(
        cloud_account: str, details: NetworkDetails
    ) -> Optional[Network]:
        details.name = details.name.strip()
        if not details.name:
            raise MissingMandatoryParamError("A network name is required")

        project_id = OpenstackIdentity.find_project(
            cloud_account, project_identifier=details.project_identifier
        )
        if not project_id:
            raise ItemNotFoundError("The specified project was not found")

        with OpenstackConnection(cloud_account) as conn:
            return conn.network.create_network(
                project_id=project_id,
                name=details.name,
                description=details.description,
                provider_network_type=details.provider_network_type,
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
        elif action is RbacNetworkActions.EXTERNAL:
            return "access_as_external"
        else:
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
        network_id = self.find_network(
            cloud_account, network_identifier=rbac_details.network_identifier
        )
        if not network_id:
            raise ItemNotFoundError("The specified network was not found")

        project_id = OpenstackIdentity.find_project(
            cloud_account, project_identifier=rbac_details.project_identifier
        )
        if not project_id:
            raise ItemNotFoundError("The specified project was not found")

        with OpenstackConnection(cloud_account) as conn:
            return conn.network.create_rbac_policy(
                object_id=network_id,
                target_project_id=project_id,
                action=self._parse_rbac_action(rbac_details.action),
            )

    def delete_network(self, cloud_account: str, network_identifier: str) -> bool:
        """
        Deletes the specified network
        :param cloud_account: The associated credentials to use
        :param network_identifier: The name or Openstack ID to use
        :return: True if deleted, else False
        """
        network_id = self.find_network(cloud_account, network_identifier)
        if not network_id:
            return False

        with OpenstackConnection(cloud_account) as conn:
            result = conn.network.delete_network(network_id, ignore_missing=False)
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

        with OpenstackConnection(cloud_account) as conn:
            result = conn.network.delete_rbac_policy(rbac_id, ignore_missing=False)
            return result is None
