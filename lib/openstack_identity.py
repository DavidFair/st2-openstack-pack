from typing import Optional

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
                description=project_details.description,
                domain_id=project_details.domain_id,
                is_enabled=project_details.is_enabled,
            )
