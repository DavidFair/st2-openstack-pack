from typing import Optional

from openstack.exceptions import ConflictException
from openstack.identity.v3.project import Project
from openstack.identity.v3.user import User

from enums.user_domains import UserDomains
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from structs.project_details import ProjectDetails


class OpenstackIdentity(OpenstackWrapperBase):
    def create_project(
        self, cloud_account: str, project_details: ProjectDetails
    ) -> Optional[Project]:
        """
        Creates a given project with the provided details
        :param cloud_account: The clouds entry to use
        :param project_details: A datastructure containing all the project details
        :return: A clouds project, or None if it was unsuccessful
        """
        # domain_id can be blank, we will create a project in the default domain
        if not project_details.name:
            raise MissingMandatoryParamError("The project name is missing")

        with self._connection_cls(cloud_account) as conn:
            try:
                return conn.identity.create_project(
                    name=project_details.name,
                    # This is intentionally hard-coded as it's very rare we create something in another domain
                    domain_id="default",
                    description=project_details.description,
                    is_enabled=project_details.is_enabled,
                )
            except ConflictException as err:
                # Strip out frames that are noise by rethrowing
                raise ConflictException(err.message) from err

    def delete_project(self, cloud_account: str, project_identifier: str) -> bool:
        """
        Deletes a project from Openstack default domain
        :param cloud_account: The clouds entry to use
        :param project_identifier: The name or Openstack ID for the project
        :return: True if the project was deleted, False if the operation failed
        """
        project = self.find_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )
        if not project:
            return False

        with self._connection_cls(cloud_account) as conn:
            result = conn.identity.delete_project(project=project, ignore_missing=False)
            return result is None  # Where None == success

    def find_mandatory_project(
        self, cloud_account: str, project_identifier: str
    ) -> Project:
        """
        Finds a property or throws a ItemNotFoundError
        :param cloud_account: The clouds entry to use
        :param project_identifier: The name or Openstack ID for the project
        :return: The found project, or raises a ItemNotFoundError
        """
        found = self.find_project(cloud_account, project_identifier)
        if found:
            return found
        raise ItemNotFoundError("The specified project was not found")

    def find_project(
        self, cloud_account: str, project_identifier: str
    ) -> Optional[Project]:
        """
        Finds a project with the given name or ID
        :param cloud_account: The clouds entry to use
        :param project_identifier: The name or Openstack ID for the project
        :return: The found project, or None
        """
        project_identifier = project_identifier.strip()
        if not project_identifier:
            raise MissingMandatoryParamError(
                "A project name or project ID must be provided"
            )

        with self._connection_cls(cloud_account) as conn:
            return conn.identity.find_project(project_identifier, ignore_missing=True)

    def find_user(
        self, cloud_account: str, user_identifier: str, user_domain: UserDomains
    ) -> Optional[User]:
        """
        Finds a user with the given name or ID
        :param cloud_account: The clouds entry to use
        :param user_identifier: The name or Openstack ID for the user
        :param user_domain: The domain to search for the user in
        :return: The found user, or None
        """
        user_identifier = user_identifier.strip()
        if not user_identifier:
            raise MissingMandatoryParamError("A user name or ID must be provided")

        domain = user_domain.value.lower().strip()
        if not domain:
            raise MissingMandatoryParamError("A domain name or ID must be provided")

        with self._connection_cls(cloud_account) as conn:
            domain_id = conn.identity.find_domain(domain, ignore_missing=False)

            return conn.identity.find_user(
                user_identifier, domain_id=domain_id.id, ignore_missing=True
            )
