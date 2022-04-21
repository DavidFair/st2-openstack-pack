from typing import Dict

from openstack.exceptions import ResourceNotFound

from openstack_action import OpenstackAction
from openstack_identity import OpenstackIdentity


class NetworkAction(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._api: OpenstackIdentity = config.get("openstack_api", OpenstackIdentity())

        # lists possible functions that could be run as an action
        self.func = {
            "network_show": self.network_show,
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
    def network_show(self, network):
        """
        Show Network Properties
        :param network: Network Name or ID
        :return: (status (Bool), reason/output (String/Dict)
        """
        try:
            network = self.conn.compute.find_hypervisor(network, ignore_missing=False)
        except ResourceNotFound as err:
            return False, f"Network not found {repr(err)}"
        return True, network

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
        self, object_type, rbac_object, target_project, **network_kwargs
    ):
        """
        Create RBAC rules
        :param object_type (String): rbac_object resource type
        :param rbac_object (String): ID or Name
        :param target_project (String): ID or Name
        :param network_kwargs - Network properties to pass in - see action definintion yaml file for details)
        :return: (status (Bool), reason (String))
        """

        # get rbac_object ID
        if object_type.lower() == "network":
            object_id = self.find_resource_id(
                rbac_object, self.conn.network.find_network
            )
            if not object_id:
                return False, f"No network found with name or ID {rbac_object}"
        else:
            return False, "Currently only allowing network as valid rbac type"

        # get project ID
        target_project_id = self.find_resource_id(
            target_project, self.conn.identity.find_project
        )
        if not target_project_id:
            return False, f"No project found with name or ID {target_project}"

        try:
            rbac = self.conn.network.create_rbac_policy(
                object_id=object_id,
                target_project_id=target_project_id,
                **network_kwargs,
            )
        except ResourceNotFound as err:
            return False, f"RBAC policy creation failed {err}"
        return True, rbac

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
