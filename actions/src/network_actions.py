from typing import Dict, Union, Tuple

from openstack.exceptions import ResourceNotFound
from openstack.network.v2.network import Network
from openstack.network.v2.rbac_policy import RBACPolicy

from enums.rbac_network_actions import RbacNetworkActions
from openstack_action import OpenstackAction
from openstack_network import OpenstackNetwork
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

    def network_create(self, project, **network_kwargs):
        """
        Create a Network for a Project
        :param project: Project Name or ID that network will be created on
        :param network_kwargs: Network properties to pass in - see action definintion yaml file for details)
        :return: (status (Bool), reason (String))
        """
        # get project id
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        if not project_id:
            return False, "Project not found"

        try:
            network = self.conn.network.create_network(
                project_id=project_id, **network_kwargs
            )
        except ResourceNotFound as err:
            return False, f"Network creation failed: {err}"
        return True, network

    def network_rbac_create(
        self,
        cloud_account: str,
        network_identifier: str,
        project_identifier: str,
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
