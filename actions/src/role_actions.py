from typing import Dict, Callable, Tuple

from st2common.runners.base_action import Action

from enums.user_domains import UserDomains
from openstack_api.openstack_roles import OpenstackRoles
from structs.role_details import RoleDetails


class RoleActions(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        # DI handled in OpenstackActionTestCase
        super().__init__(*args, config=config, **kwargs)
        self._api: OpenstackRoles = config.get("openstack_api", OpenstackRoles())

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches
        :param submodule: the method to run
        :param kwargs: Arguments to the method
        :return: The output from that method
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    # TODO Show all roles on a project
    # pylint: disable=duplicate-code, too-many-arguments
    def role_add(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role: str,
        user_domain: str,
    ) -> bool:
        """
        Add a given user a project role
        :param cloud_account: The account from the clouds configuration to use
        :param user_identifier: Name or ID of the user to assign a role to
        :param project_identifier: Name or ID of the project this applies to
        :param role: Name or ID of the role to assign
        :param user_domain: The domain the user is associated with
        :return: status
        """
        details = RoleDetails(
            user_identifier=user_identifier,
            project_identifier=project_identifier,
            role_identifier=role,
            user_domain=UserDomains.from_string(user_domain),
        )
        self._api.assign_role_to_user(cloud_account=cloud_account, details=details)
        return True  # the above method always returns None

    # pylint: disable=duplicate-code, too-many-arguments
    def role_remove(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role: str,
        user_domain: str,
    ) -> bool:
        """
        Removes a project role from a given user
        :param cloud_account: The account from the clouds configuration to use
        :param user_identifier: Name or ID of the user to remove a role from
        :param project_identifier: Name or ID of the project this applies to
        :param role: Name or ID of the role to remove
        :param user_domain: The domain the user is associated with
        :return: status
        """
        details = RoleDetails(
            user_identifier=user_identifier,
            project_identifier=project_identifier,
            role_identifier=role,
            user_domain=UserDomains.from_string(user_domain),
        )
        self._api.remove_role_from_user(cloud_account=cloud_account, details=details)
        return True

    # pylint: disable=duplicate-code, too-many-arguments
    def user_has_role(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role: str,
        user_domain: str,
    ) -> Tuple[bool, str]:
        """
        Checks a given user has the specified role
        :param cloud_account: The account from the clouds configuration to use
        :param user_identifier: Name or ID of the user to check
        :param project_identifier: Name or ID of the project this applies to
        :param role: Name or ID of the role to check
        :param user_domain: The domain the user is associated with
        :return: If the user has the role (bool)
        """
        details = RoleDetails(
            user_identifier=user_identifier,
            project_identifier=project_identifier,
            role_identifier=role,
            user_domain=UserDomains.from_string(user_domain),
        )
        found = self._api.has_role(cloud_account=cloud_account, details=details)
        out = (
            "The user has the specified role"
            if found
            else "The user does not have the specified role"
        )
        return bool(found), out
