from typing import Tuple

from openstack.identity.v3.project import Project
from openstack.identity.v3.role import Role
from openstack.identity.v3.user import User

from enums.user_domains import UserDomains
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenstackRoles(OpenstackWrapperBase):
    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(connection_cls)

    def _find_role_details(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role_identifier: str,
        user_domain: UserDomains,
    ) -> Tuple[User, Project, Role]:
        """
        Finds the various OS objects required for role manipulation
        """
        project = self._identity_api.find_mandatory_project(
            cloud_account, project_identifier
        )
        user = self._identity_api.find_user(cloud_account, user_identifier, user_domain)
        role = self.find_role(cloud_account, role_identifier)

        if not user:
            raise ItemNotFoundError("The requested user could not be found")
        if not role:
            raise ItemNotFoundError("The requested role could not be found")

        return user, project, role

    def assign_role_to_user(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role_identifier: str,
        user_domain: UserDomains,
    ) -> None:
        """
        Assigns a given role to the specified user
        :param cloud_account: The account from the clouds configuration to use
        :param user_identifier: Name or ID of the user to assign a role to
        :param project_identifier: Name or ID of the project this applies to
        :param role_identifier: Name or ID of the role to assign
        :param user_domain: The realm the user can be found in
        """
        user, project, role = self._find_role_details(
            cloud_account,
            user_identifier,
            project_identifier,
            role_identifier,
            user_domain,
        )

        with self._connection_cls(cloud_account) as conn:
            conn.identity.assign_project_role_to_user(
                project=project, user=user, role=role
            )

    def find_role(self, cloud_account: str, role_identifier: str) -> Role:
        """
        Finds a given role based on an identifier
        :param cloud_account: The account from the clouds configuration to use
        :param role_identifier: Name or ID of the role to find
        """
        role_identifier = role_identifier.strip()
        if not role_identifier:
            raise MissingMandatoryParamError("A role name or ID is required")

        with self._connection_cls(cloud_account) as conn:
            return conn.identity.find_role(role_identifier, ignore_missing=True)

    def has_role(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role_identifier: str,
        user_domain: UserDomains,
    ) -> bool:
        """
        Checks if the specified user has the given role
        :param cloud_account: The account from the clouds configuration to use
        :param user_identifier: Name or ID of the user to assign a role to
        :param project_identifier: Name or ID of the project this applies to
        :param role_identifier: Name or ID of the role to assign
        :param user_domain: The user domain the account is associated with
        """
        user, project, role = self._find_role_details(
            cloud_account,
            user_identifier,
            project_identifier,
            role_identifier,
            user_domain,
        )

        # Note: this changed as of commit
        # https://github.com/openstack/openstacksdk/commit/95cec28723a7b1a66b2b6a34aefcb2660140d81c
        with self._connection_cls(cloud_account) as conn:
            return conn.identity.validate_user_has_role(
                project=project, user=user, role=role
            )

    def remove_role_from_user(
        self,
        cloud_account: str,
        user_identifier: str,
        project_identifier: str,
        role_identifier: str,
        user_domain: UserDomains,
    ) -> None:
        """
        Assigns a given role to the specified user
        :param cloud_account: The account from the clouds configuration to use
        :param user_identifier: Name or ID of the user to assign a role to
        :param project_identifier: Name or ID of the project this applies to
        :param role_identifier: Name or ID of the role to assign
        :param user_domain: The user domain the account is associated with
        """
        user, project, role = self._find_role_details(
            cloud_account,
            user_identifier,
            project_identifier,
            role_identifier,
            user_domain,
        )
        with self._connection_cls(cloud_account) as conn:
            conn.identity.unassign_project_role_from_user(
                project=project, user=user, role=role
            )
