from typing import Dict, Union, Tuple, Optional

from openstack.exceptions import ResourceNotFound
from openstack.network.v2.network import Network
from openstack.network.v2.rbac_policy import RBACPolicy

from enums.network_providers import NetworkProviders
from enums.rbac_network_actions import RbacNetworkActions
from openstack_action import OpenstackAction
from openstack_network import OpenstackNetwork
from structs.network_details import NetworkDetails
from structs.network_rbac import NetworkRbac


class NetworkActions(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._api: OpenstackNetwork = config.get("openstack_api", OpenstackNetwork())

        # lists possible functions that could be run as an action
        self.func = {
            "network_find": self.network_find,
            "network_rbac_show": self.network_rbac_show,
            "network_rbac_create": self.network_rbac_create,
            "network_create": self.network_create,
            "network_delete": self.network_delete,
            "network_rbac_delete": self.network_rbac_delete
            # network_update
            # network_rbac_update
        }

    # TODO:
    # network show
    # network rbac show
    # network delete
    # network rbac delete
    def network_find(
        self, cloud_account: str, network_identifier: str
    ) -> Tuple[bool, Union[Network, str]]:
        """
        Show Network Properties
        :param cloud_account: The account from the clouds configuration to use
        :param network_identifier: Network Name or ID
        :return: (status (Bool), reason/output (String/Dict)
        """
        network = self._api.find_network(cloud_account, network_identifier)
        output = network if network else "The requested network could not be found"
        return bool(network), output

    def network_rbac_show(self, rbac_policy):
        """
        Show Network RBAC policy
        :param rbac_policy: RBAC Name or ID
        :return:(status (Bool), reason/output (String/Dict)
        """
        try:
            rbac_policy = self.conn.network.find_rbac_policy(
                rbac_policy, ignore_missing=False
            )
        except ResourceNotFound as err:
            return False, f"RBAC policy not found, {err}"
        return True, rbac_policy

    def network_create(
        self,
        cloud_account: str,
        project_identifier: str,
        network_name: str,
        network_description: str,
        provider_network_type: str,
        port_security_enabled: bool,
        has_external_router: bool,
    ) -> Tuple[bool, Optional[Network]]:
        """
        Creates a network for a given project
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: Name or Openstack ID to use for the project
        :param network_name: The new network name
        :param network_description: The new network description
        :param provider_network_type: The type of underlying physical network to map to
        :param port_security_enabled: Whether to enable port security on this network
        :param has_external_router: Is this network the default external network
        :return: The created network object, if any
        """

        network_type = NetworkProviders[provider_network_type]
        details = NetworkDetails(
            name=network_name,
            description=network_description,
            project_identifier=project_identifier,
            provider_network_type=network_type,
            port_security_enabled=port_security_enabled,
            has_external_router=has_external_router,
        )

        network = self._api.create_network(cloud_account, details)
        return bool(network), network

    def network_rbac_create(
        self,
        cloud_account: str,
        project_identifier: str,
        network_identifier: str,
        rbac_action: str,
    ) -> Tuple[bool, RBACPolicy]:
        """
        Create RBAC rules
        :param cloud_account: The account from the clouds configuration to use
        :param network_identifier: Name or Openstack ID for the network
        :param project_identifier: Name or Openstack ID for the project
        :param rbac_action: - Network properties to pass in - see action definintion yaml file for details)
        :return: status, Policy Object
        """
        action_enum = RbacNetworkActions[rbac_action.upper()]
        rbac_details = NetworkRbac(
            name="",
            action=action_enum,
            project_identifier=project_identifier,
            network_identifier=network_identifier,
        )

        rbac = self._api.create_network_rbac(cloud_account, rbac_details)
        return bool(rbac), rbac

    def network_delete(self, network, project):
        """
        Delete a Network
        :param network: Name or ID
        :param project: Name or ID
        :return: (status (Bool), reason (String))
        """
        raise NotImplementedError

    def network_rbac_delete(self, rbac_policy):
        """
        Delete a Network RBAC rule
        :param rbac_policy: Name or ID
        :return: (status (Bool), reason (String))
        """
        raise NotImplementedError
