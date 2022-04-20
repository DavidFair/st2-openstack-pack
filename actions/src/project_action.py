from typing import Tuple, Optional

from openstack.exceptions import ResourceNotFound
from openstack.identity.v3.project import Project

from openstack_action import OpenstackAction
from openstack_identity import OpenstackIdentity
from structs.create_project import ProjectDetails


class ProjectAction(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)

        # DI handled in OpenstackActionTestCase
        self._api: OpenstackIdentity = kwargs["config"].get(
            "openstack_api", OpenstackIdentity()
        )

        # lists possible functions that could be run as an action
        self.func = {
            "project_show": self.project_show,
            "project_create": self.project_create,
            "project_delete": self.project_delete,
        }

    def project_delete(self, project):
        """
        Delete a project
        :param project: project Name or ID
        :return: (status (Bool), reason (String))
        """
        raise NotImplementedError

    def project_show(self, cloud_account: str, domain: str, project: str):
        """
        find and return a given project's properties
        :param cloud_account: The account from the clouds configuration to use
        :param project:(String) Name or ID,
        :param domain:(String) DomainAction Name or ID
        :return: (status (Bool), reason (String))
        """
        raise NotImplementedError("Not implemented yet")
        domain_id = self.find_domain(cloud_account, domain)
        # pylint: disable=unreachable
        if not domain_id:
            return False, f"No domain found with Name or ID {domain}"
        # TODO:
        try:
            project = self.conn.identity.find_project(project, domain_id=domain_id)
        except ResourceNotFound as err:
            return False, f"Finding Project Failed {err}"
        return True, project

    def project_create(
        self,
        cloud_account: str,
        name: str,
        description: str,
        is_enabled: bool,
    ) -> Tuple[bool, Optional[Project]]:
        """
        Find and return a given project's properties. Expected
        to be called within a workflow and not directly.
        :param: cloud_account: The account from the clouds configuration to use
        :param: name: Name of new project
        :param: description: Description for new project
        :param: is_enabled: Set if new project enabled or disabled
        :return: status, optional project
        """
        details = ProjectDetails(
            name=name,
            description=description,
            # This is intentionally hard-coded as it's very rare we create something in another domain
            domain_id="default",
            is_enabled=is_enabled,
        )
        project = self._api.create_project(
            cloud_account=cloud_account, project_details=details
        )
        return bool(project), project
