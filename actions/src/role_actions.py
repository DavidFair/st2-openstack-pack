from typing import Dict

from openstack.exceptions import ResourceNotFound

from openstack_action import OpenstackAction
from openstack_api.openstack_roles import OpenstackRoles


class RoleActions(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        # DI handled in OpenstackActionTestCase
        super().__init__(*args, config=config, **kwargs)
        self._api: OpenstackRoles = config.get("openstack_api", OpenstackRoles())

        # lists possible functions that could be run as an action
        self.func = {
            "role_add": self.role_add,
            "role_remove": self.role_remove,
            "role_validate_user": self.validate_user
            # role update
        }

    # TODO Show all roles on a project

    # pylint: disable=missing-function-docstring
    def get_ids(self, role, project, user_domain, user):
        role_id = self.find_resource_id(role, self.conn.identity.find_role)
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        user_domain_id = self.find_resource_id(
            user_domain, self.conn.identity.find_domain
        )
        user_id = self.find_resource_id(
            user, self.conn.identity.find_user, domain_id=user_domain_id
        )
        return role_id, project_id, user_id

    def role_add(self, role, project, user_domain, user):
        """
        Add User Role to Project
        :param role: (String) Name or ID
        :param project: (String) Name or ID
        :param user_domain: (String) Name or ID,
        :param user: (String) Name or ID
        :return: (status (Bool), reason (String))
        """
        role_id, project_id, user_id = self.get_ids(role, project, user_domain, user)
        try:
            role_assignment = self.conn.identity.assign_project_role_to_user(
                project_id, user_id, role_id
            )
        except ResourceNotFound as err:
            return False, f"Role Assignment Failed {err}"
        return True, role_assignment

    def role_remove(self, role, project, user_domain, user):
        """
        Remove User Role to Project
        :param role: (String) Name or ID
        :param project: (String) Name or ID
        :param user_domain: (String) Name or ID,
        :param user: (String) Name or ID
        :return: (status (Bool), reason (String))
        """
        role_id, project_id, user_id = self.get_ids(role, project, user_domain, user)
        try:
            role_assignment = self.conn.identity.unassign_project_role_from_user(
                project_id, user_id, role_id
            )
        except ResourceNotFound as err:
            return False, f"Role Assignment Failed {err}"
        return True, role_assignment

    def validate_user(self, role, project, user_domain, user):
        """
        Validate User Role to Project
        :param role: (String) Name or ID
        :param project: (String) Name or ID
        :param user_domain: (String) Name or ID,
        :param user: (String) Name or ID
        :return: (status (Bool), reason (String))
        """
        role_id, project_id, user_id = self.get_ids(role, project, user_domain, user)
        try:
            exists_bool = self.conn.identity.validate_user_has_role(
                project_id, user_id, role_id
            )
        except ResourceNotFound as err:
            return False, f"Validation Failed {err}"
        return True, exists_bool
