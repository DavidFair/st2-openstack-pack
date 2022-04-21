from typing import Optional

from openstack.exceptions import ResourceNotFound
from openstack.identity.v3.project import Project
from missing_mandatory_param_error import MissingMandatoryParamError
from openstack_connection import OpenstackConnection
from structs.create_project import ProjectDetails


class OpenstackIdentity:
    @staticmethod
    def create_project(
        cloud_account: str, project_details: ProjectDetails
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

        with OpenstackConnection(cloud_account) as conn:
            return conn.identity.create_project(
                name=project_details.name,
                # This is intentionally hard-coded as it's very rare we create something in another domain
                domain_id="default",
                description=project_details.description,
                is_enabled=project_details.is_enabled,
            )

    @staticmethod
    def delete_project(cloud_account: str, project_identifier: str) -> bool:
        """
        Deletes a project from Openstack default domain
        :param cloud_account: The clouds entry to use
        :param project_identifier: The name or Openstack ID for the project
        :return: True if the project was deleted, False if the operation failed
        """
        project_identifier = project_identifier.strip()
        if not project_identifier:
            raise MissingMandatoryParamError(
                "A project name or project ID must be provided"
            )

        ignore_missing = False
        with OpenstackConnection(cloud_account) as conn:
            try:
                result = conn.identity.delete_project(
                    project=project_identifier, ignore_missing=ignore_missing
                )
                return result is None  # Where None == success
            except ResourceNotFound:
                return False

    @staticmethod
    def find_project(cloud_account: str, project_identifier: str) -> Optional[Project]:
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

        with OpenstackConnection(cloud_account) as conn:
            return conn.identity.find_project(project_identifier, ignore_missing=True)
