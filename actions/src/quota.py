from openstack.exceptions import ResourceNotFound

from openstack_action import OpenstackAction


class Quote(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {"quota_set": self.quota_set, "quota_show": self.quota_show}

    def quota_set(self, project, **quota_kwargs):
        """
        Set a project's quota
        :param project (String): ID or Name
        :param quota_kwargs - see action definition yaml file for details)
        :return: (status (Bool), reason (String))
        """
        # get project id
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        if not project_id:
            return False, f"Project not found with Name or ID {project}"

        try:
            # quota ID is same as project ID
            quota = self.conn.network.update_quota(quota=project_id, **quota_kwargs)
        except ResourceNotFound as err:
            return False, f"Quota update failed {err}"
        return True, quota

    def quota_show(self, project):
        """
        Show a project's quota
        :param project: ID or Name
        :return: (status (Bool), reason (String))
        """
        # get project id
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        if not project_id:
            return False, f"Project not found with Name or ID {project}"
        try:
            # quota ID is same as project ID
            quota = self.conn.network.get_quota(quota=project_id, details=True)
        except ResourceNotFound as err:
            return False, f"Quota not found {err}"
        return True, quota
