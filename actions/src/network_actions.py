from typing import Dict, Union, Tuple, Optional, Callable

from openstack.network.v2.network import Network
from openstack.network.v2.rbac_policy import RBACPolicy
from st2common.runners.base_action import Action

from enums.network_providers import NetworkProviders
from enums.rbac_network_actions import RbacNetworkActions
from openstack_network import OpenstackNetwork
from structs.network_details import NetworkDetails
from structs.network_rbac import NetworkRbac


class NetworkActions(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._api: OpenstackNetwork = config.get("openstack_api", OpenstackNetwork())

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    # Pending:
    # network_update
    # network_rbac_update

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

    def network_rbac_find(
        self, cloud_account: str, rbac_identifier: str
    ) -> Tuple[bool, Union[RBACPolicy, str]]:
        """
        Finds a given Network RBAC policy
        :param cloud_account: The account from the clouds configuration to use
        :param rbac_identifier: RBAC Name or ID
        :return: status, RBAC Policy object or error message
        """
        policy = self._api.find_network_rbac(cloud_account, rbac_identifier)
        output = policy if policy else "The requested policy could not be found"
        return bool(policy), output

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

    def network_delete(
        self, cloud_account: str, network_identifier: str
    ) -> Tuple[bool, str]:
        """
        Deletes the specified network
        :param cloud_account: The account from the clouds.yaml configuration to use
        :param network_identifier: The network name or Openstack ID to remove
        :return: If the network was deleted, error message if any
        """
        result = self._api.delete_network(cloud_account, network_identifier)
        err = "" if result else "The selected network could not be found"
        return result, err

    def network_rbac_delete(
        self, cloud_account: str, rbac_identifier: str
    ) -> Tuple[bool, str]:
        """
        Removes a given Network RBAC policy
        :param cloud_account: The account from the clouds configuration to use
        :param rbac_identifier: RBAC Name or Openstack ID
        :return: status, RBAC Policy object or error message
        """
        result = self._api.delete_network_rbac(cloud_account, rbac_identifier)
        err = "" if result else "The selected RBAC policy could not be found"
        return result, err
