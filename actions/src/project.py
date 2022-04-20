from openstack.exceptions import ResourceNotFound

from openstack_action import OpenstackAction
from openstack_identity import OpenstackIdentity


class Project(OpenstackAction):
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

    def project_create(self, domain, name, description, is_enabled):
        """
        find and return a given project's properties
        :param domain: (String) Name or ID,
        :param name: (String) Name of new project
        :param description: (String) Description for new project
        :param is_enabled: (Bool) Set if new project enabled or disabled
        :return: (status (Bool), reason (String))
        """

        domain_id = self.find_resource_id(domain, self.conn.identity.find_domain)
        if not domain_id:
            return False, f"No domain found with Name or ID {domain}"
        try:
            project = self.conn.identity.create_project(
                domain_id=domain_id,
                name=name,
                description=description,
                is_enabled=is_enabled,
            )
        except ResourceNotFound as err:
            return False, f"Project Creation Failed {err}"
        return True, project
