from typing import Dict, Tuple, Optional

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
            "user_has_role": self.user_has_role
            # role update
        }

    # TODO Show all roles on a project
    def role_add(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role_identifier: str,
    ) -> bool:
        """
        Add a given user a project role
        :param cloud_account: The account from the clouds configuration to use
        :param user_identifier: Name or ID of the user to assign a role to
        :param project_identifier: Name or ID of the project this applies to
        :param role_identifier: Name or ID of the role to assign
        :return: status
        """
        self._api.assign_role_to_user(
            cloud_account=cloud_account,
            user_identifier=user_identifier,
            project_identifier=project_identifier,
            role_identifier=role_identifier,
        )
        return True  # the above method always returns None

    def role_remove(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role_identifier: str,
    ) -> bool:
        """
        Removes a project role from a given user
        :param cloud_account: The account from the clouds configuration to use
        :param user_identifier: Name or ID of the user to remove a role from
        :param project_identifier: Name or ID of the project this applies to
        :param role_identifier: Name or ID of the role to remove
        :return: status
        """
        self._api.remove_role_from_user(
            cloud_account=cloud_account,
            user_identifier=user_identifier,
            project_identifier=project_identifier,
            role_identifier=role_identifier,
        )
        return True

    def user_has_role(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role_identifier: str,
    ) -> bool:
        """
        Checks a given user has the specified role
        :param cloud_account: The account from the clouds configuration to use
        :param user_identifier: Name or ID of the user to check
        :param project_identifier: Name or ID of the project this applies to
        :param role_identifier: Name or ID of the role to check
        :return: If the user has the role (bool)
        """
        return self._api.has_role(
            cloud_account=cloud_account,
            user_identifier=user_identifier,
            project_identifier=project_identifier,
            role_identifier=role_identifier,
        )
