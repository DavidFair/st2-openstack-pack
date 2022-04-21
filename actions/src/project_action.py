from typing import Tuple, Optional, Dict, Callable

from openstack.identity.v3.project import Project

from openstack_identity import OpenstackIdentity
from structs.create_project import ProjectDetails
from st2common.runners.base_action import Action


class ProjectAction(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        # DI handled in OpenstackActionTestCase
        super().__init__(*args, config, **kwargs)
        self._api: OpenstackIdentity = config.get("openstack_api", OpenstackIdentity())

        # lists possible functions that could be run as an action
        self.func = {
            "project_find": self.project_find,
            "project_create": self.project_create,
            "project_delete": self.project_delete,
        }

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches
        :param submodule: the method to run
        :param kwargs: Arguments to the method
        :return: The output from that method
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def project_delete(
        self, cloud_account: str, project_identifier: str
    ) -> Tuple[bool, str]:
        """
        Deletes a project
        :param: cloud_account: The account from the clouds configuration to use
        :param: project_name: (Either) The project name to delete
        :param: project_id: (Either) The project ID to delete
        :return: The result of the operation
        """
        delete_ok = self._api.delete_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )
        # Currently, we only handle one error, other throws will propagate upwards
        err = "" if delete_ok else "The specified project was not found"
        return delete_ok, err

    def project_find(
        self, cloud_account: str, project_identifier: str
    ) -> Tuple[bool, Optional[Project]]:
        """
        find and return a given project's properties
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: Name or Openstack ID
        :return: (status (Bool), reason (String))
        """
        project = self._api.find_project(
            cloud_account=cloud_account, project_identifier=project_identifier
        )
        return bool(project), project

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
            name=name, description=description, is_enabled=is_enabled
        )
        project = self._api.create_project(
            cloud_account=cloud_account, project_details=details
        )
        return bool(project), project
