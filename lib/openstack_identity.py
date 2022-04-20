from typing import Optional

from openstack.exceptions import ResourceNotFound
from openstack.identity.v3.project import Project
from missing_mandatory_param_error import MissingMandatoryParamError
from openstack_connection import OpenstackConnection

# pylint: disable=too-few-public-methods
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
    def delete_project(cloud_account: str, project_details: ProjectDetails) -> bool:
        """
        :param cloud_account: The clouds entry to use
        :param project_details: A datastructure containing all the project details
        :return: True if the project was deleted, False if the operation failed
        """
        proj_identifier = (
            project_details.name.strip() if project_details.name.strip() else None
        )
        proj_identifier = (
            project_details.openstack_id.strip()
            if project_details.openstack_id
            else proj_identifier
        )

        if not proj_identifier:
            raise MissingMandatoryParamError(
                "A project name or project ID must be provided"
            )

        ignore_missing = False
        with OpenstackConnection(cloud_account) as conn:
            try:
                result = conn.identity.delete_project(
                    project=proj_identifier, ignore_missing=ignore_missing
                )
                return result is None  # Where None == success
            except ResourceNotFound:
                return False
