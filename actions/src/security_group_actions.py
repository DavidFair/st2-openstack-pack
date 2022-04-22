import os
from subprocess import Popen, PIPE
from typing import Dict, Tuple, Union, Optional

from openstack.exceptions import ResourceNotFound, ConflictException
from openstack.network.v2.security_group import SecurityGroup

from openstack_action import OpenstackAction
from openstack_api.openstack_security_groups import OpenstackSecurityGroups


class SecurityGroupActions(OpenstackAction):
    def __init__(self, *args, config: Dict, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._api: OpenstackSecurityGroups = config.get(
            "openstack_api", OpenstackSecurityGroups()
        )

        # lists possible functions that could be run as an action
        self.func = {
            "security_group_create": self.security_group_create,
            "security_group_rule_create": self.security_group_rule_create,
            "security_group_show": self.security_group_find,
            "security_group_list": self.security_group_list
            # security_group_delete
            # security_group_update
        }

    def security_group_create(
        self,
        cloud_account: str,
        group_name: str,
        group_description: str,
        project_identifier: str,
    ) -> Tuple[bool, SecurityGroup]:
        """
        Create a Security Group for a Project
        :param cloud_account: The associated clouds.yaml account
        :param group_name: The new name for the security group
        :param group_description: The description to associate with the new group
        :param project_identifier: Openstack Project ID or Name,
        :return: status, the new Security group or None
        """
        security_group = self._api.create_security_group(
            cloud_account, group_name, group_description, project_identifier
        )
        return bool(security_group), security_group

    def security_group_find(
        self,
        cloud_account: str,
        project_identifier: str,
        security_group_identifier: str,
    ) -> Tuple[bool, Union[SecurityGroup, str]]:
        """
        Show a security group
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: Openstack Project ID or Name,
        :param security_group_identifier: Openstack Security Group ID or Name
        :return: status, Security Group object or error message
        """
        security_group = self._api.find_security_group(
            cloud_account, project_identifier, security_group_identifier
        )
        output = (
            security_group
            if security_group
            else "The requested security group could not be found"
        )
        return bool(security_group), output

    def security_group_list(self, project):
        """
        List Security groups for a project
        :param project:(String) Name or ID
        :return: (status (Bool), reason (String))
        """
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        if not project_id:
            return False, f"Project not found with Name or ID {project}"

        # needs to be called when creating new project, openstacksdk fails to find security groups unless this is called
        with (
            Popen(
                SOURCECMD
                + f"openstack security group list --project {project_id} -f json",
                shell=True,
                stdout=PIPE,
                env=os.environ.copy(),
            )
        ) as process_handle:
            _ = process_handle.communicate()[0]

        try:
            security_groups = self.conn.network.security_groups(project_id=project_id)
            all_groups = []
            for group in security_groups:
                all_groups.append(group)
        except ResourceNotFound as err:
            return False, f"Listing Security Groups Failed {err}"
        return True, all_groups

    def security_group_rule_create(
        self, security_group, project, dst_port, **security_group_kwargs
    ):
        """
        Creature security group rule
        :param security_group: (String) Name or ID
        :param project: (String) Name or ID,
        :param dst_port: (String: <Int>:<Int>) Min and Max port range,
        :param security_group_kwargs: other_args - see action definintion yaml file for details
        :return: (status (Bool), reason (String))
        """

        # get project id
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        if not project_id:
            return False, f"Project not found with Name or ID {project}"

        # get security group id
        security_group_id = self.find_resource_id(
            security_group, self.conn.network.find_security_group, project_id=project_id
        )
        if not security_group_id:
            return (
                False,
                f"Security group not found with Name or ID {security_group} for Project {project}",
            )

        # get min and max port ranges
        if dst_port:
            port_range_min, port_range_max = dst_port.split(":")
        else:
            port_range_min, port_range_max = None, None

        try:
            security_group_rule = self.conn.network.create_security_group_rule(
                project_id=project_id,
                security_group_id=security_group_id,
                port_range_max=port_range_max,
                port_range_min=port_range_min,
                **security_group_kwargs,
            )
        except ConflictException:
            return (
                True,
                f"Security Group Rule direction={security_group_kwargs['direction']},"
                f" ether_type={security_group_kwargs['ether_type']},"
                f" protocol=security_group_kwargs['protocol'],"
                f" remote_ip_prefix={security_group_kwargs['remote_ip_prefix']},"
                f" dst_port={port_range_max}:{port_range_min}"
                f" exist for project {project_id}",
            )
        except ResourceNotFound as err:
            return False, f"Security group rule creation failed {err}"
        return True, security_group_rule
