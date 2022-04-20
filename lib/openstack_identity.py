from typing import Optional

from openstack.identity.v3.domain import Domain
from openstack.identity.v3.project import Project

from missing_mandatory_param_error import (
    MissingMandatoryParamError,
)
from openstack_connection import OpenstackConnection

# pylint: disable=too-few-public-methods
from structs.create_project import ProjectDetails


class OpenstackIdentity:
    @staticmethod
    def find_domain(cloud_account: str, domain: str) -> Optional[Domain]:
        """
        Finds the given domain based on the UUID or name
        @param cloud_account: The clouds.yaml account to use whilst connecting
        @param domain: (str) the UUID or name of the domain to find
        @return: The domain if found, else None
        """
        if not domain:
            raise MissingMandatoryParamError("No project or domain were provided")

        with OpenstackConnection(cloud_account) as conn:
            return conn.identity.find_domain(name_or_id=domain, ignore_missing=True)

    @staticmethod
    def create_project(
        cloud_account: str, project_details: ProjectDetails
    ) -> Optional[Project]:
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
