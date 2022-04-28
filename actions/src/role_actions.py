from typing import Dict, Callable, Tuple

from st2common.runners.base_action import Action

from openstack_api.openstack_roles import OpenstackRoles


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
    # pylint: disable=duplicate-code
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

    # pylint: disable=duplicate-code
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

    # pylint: disable=duplicate-code
    def user_has_role(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role_identifier: str,
    ) -> Tuple[bool, str]:
        """
        Checks a given user has the specified role
        :param cloud_account: The account from the clouds configuration to use
        :param user_identifier: Name or ID of the user to check
        :param project_identifier: Name or ID of the project this applies to
        :param role_identifier: Name or ID of the role to check
        :return: If the user has the role (bool)
        """
        found = self._api.has_role(
            cloud_account=cloud_account,
            user_identifier=user_identifier,
            project_identifier=project_identifier,
            role_identifier=role_identifier,
        )
        out = (
            "The user has the specified role"
            if found
            else "The user does not have the specified role"
        )
        return bool(found), out
